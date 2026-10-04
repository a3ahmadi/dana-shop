import logging
from zoneinfo import ZoneInfo

from rest_framework import status
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from orders.models import Order
from .models import Payment

from .serializers import CreatePaymentSerializer
from .services import (
    create_payment,
    ZarinpalService,
    complete_payment,
)


logger = logging.getLogger(__name__)


def render_payment_result(request, template_name, payment=None, order=None, message="", http_status=200, retry=False, uncertain=False):
    if order is None and payment:
        order = payment.order
    if not request.user.is_authenticated or (order and order.user_id != request.user.id):
        order = None
    response = render(request, template_name, {
        "order": order,
        "order_items": order.items.all() if order else (),
        "payment": payment if order else None,
        "payment_date": timezone.localtime(payment.updated_at, ZoneInfo("Asia/Tehran")) if order and payment else None,
        "message": message,
        "retry": retry and order is not None,
        "uncertain": uncertain,
    }, status=http_status)
    response["Cache-Control"] = "no-store"
    return response


@method_decorator(never_cache, name="dispatch")
class PaymentStartFailureView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user, status="pending")
        payment = Payment.objects.filter(order=order).first()
        uncertain = bool(payment and payment.authority and payment.status == "pending")
        message = (
            "انتقال به درگاه کامل نشد و وضعیت تراکنش نیاز به بررسی دارد. در صورت کسر وجه، با پشتیبانی تماس بگیرید."
            if uncertain else "اتصال به درگاه انجام نشد. سفارش شما در انتظار پرداخت باقی مانده است."
        )
        return render_payment_result(
            request, "storefront/pages/fail-payment.html", payment=payment, order=order,
            message=message, retry=not uncertain, uncertain=uncertain,
        )


class CreatePaymentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CreatePaymentSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        order_id = serializer.validated_data[
            "order_id"
        ]

        order = (
            Order.objects
            .filter(
                id=order_id,
                user=request.user,
            )
            .first()
        )

        if not order:
            return Response(
                {
                    "detail": "سفارش پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if not settings.ZARINPAL_MERCHANT_ID or not settings.ZARINPAL_CALLBACK_URL:
            return Response(
                {"detail": "درگاه پرداخت هنوز پیکربندی نشده است."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:

            payment = create_payment(
                order=order,
                user=request.user,
            )

            gateway = ZarinpalService()

            payment_url = gateway.request_payment(
                payment
            )

        except ValueError as error:

            return Response(
                {
                    "detail": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:

            return Response(
                {
                    "detail": "خطا در ارتباط با درگاه پرداخت."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response(
            {
                "detail": "درخواست پرداخت با موفقیت ایجاد شد.",
                "payment": {
                    "id": payment.id,
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "amount": payment.amount,
                    "status": payment.status,
                    "authority": payment.authority,
                    "payment_url": payment_url,
                }
            },
            status=status.HTTP_201_CREATED
        )


@method_decorator(never_cache, name="dispatch")
class PaymentCallbackAPIView(APIView):

    def get(self, request):

        authority = request.query_params.get(
            "Authority"
        )

        payment_status = request.query_params.get(
            "Status"
        )

        if not authority:
            return render_payment_result(
                request, "storefront/pages/fail-payment.html",
                message="شناسهٔ پرداخت از درگاه دریافت نشد.",
                http_status=400,
            )

        payment = (
            Payment.objects
            .select_related("order")
            .filter(
                authority=authority
            )
            .first()
        )

        if not payment:
            return render_payment_result(
                request, "storefront/pages/fail-payment.html",
                message="تراکنش مورد نظر پیدا نشد. در صورت کسر وجه، با پشتیبانی تماس بگیرید.",
                http_status=404,
                uncertain=True,
            )

        if payment.status == "success":
            return render_payment_result(request, "storefront/pages/success-payment.html", payment=payment)

        if payment_status != "OK":

            payment.status = "failed"

            payment.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            payment.order.payment_status = "failed"

            payment.order.save(
                update_fields=[
                    "payment_status",
                    "updated_at",
                ]
            )

            return render_payment_result(
                request, "storefront/pages/fail-payment.html", payment=payment,
                message="پرداخت در درگاه لغو شد یا انجام نشد.", retry=True,
            )

        gateway = ZarinpalService()

        try:

            result = gateway.verify_payment(
                authority=authority,
                amount=payment.amount,
            )

        except Exception:
            logger.exception("Payment verification request failed for payment %s", payment.id)
            return render_payment_result(
                request, "storefront/pages/fail-payment.html", payment=payment,
                message="نتیجهٔ پرداخت هنوز قابل تأیید نیست. در صورت کسر وجه، با پشتیبانی تماس بگیرید.",
                http_status=503, uncertain=True,
            )

        data = result.get("data") if isinstance(result, dict) else None
        data = data if isinstance(data, dict) else {}

        code = data.get("code")

        if code is None:
            return render_payment_result(
                request, "storefront/pages/fail-payment.html", payment=payment,
                message="پاسخ معتبری از درگاه دریافت نشد. وضعیت تراکنش نیاز به بررسی دارد.",
                http_status=503, uncertain=True,
            )

        if code not in [100, 101]:

            payment.status = "failed"

            payment.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            payment.order.payment_status = "failed"

            payment.order.save(
                update_fields=[
                    "payment_status",
                    "updated_at",
                ]
            )

            return render_payment_result(
                request, "storefront/pages/fail-payment.html", payment=payment,
                message="پرداخت توسط درگاه تأیید نشد.", retry=True,
            )

        ref_id = data.get("ref_id")
        if not ref_id:
            return render_payment_result(
                request, "storefront/pages/fail-payment.html", payment=payment,
                message="شمارهٔ پیگیری از درگاه دریافت نشد. وضعیت تراکنش باید بررسی شود.",
                http_status=503, uncertain=True,
            )

        try:

            payment.ref_id = ref_id

            payment.save(
                update_fields=[
                    "ref_id",
                    "updated_at",
                ]
            )

            complete_payment(
                payment_id=payment.id,
                request=request,
            )

        except ValueError as error:
            logger.error("Verified payment %s could not complete: %s", payment.id, error)
            return render_payment_result(
                request, "storefront/pages/fail-payment.html", payment=payment,
                message="تراکنش در درگاه تأیید شد، اما ثبت نهایی سفارش انجام نشد. با پشتیبانی تماس بگیرید.",
                http_status=503, uncertain=True,
            )

        except Exception:
            logger.exception("Verified payment %s could not complete", payment.id)
            return render_payment_result(
                request, "storefront/pages/fail-payment.html", payment=payment,
                message="تراکنش در درگاه تأیید شد، اما ثبت نهایی سفارش انجام نشد. با پشتیبانی تماس بگیرید.",
                http_status=503, uncertain=True,
            )

        payment.refresh_from_db()
        return render_payment_result(request, "storefront/pages/success-payment.html", payment=payment)
