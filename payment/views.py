from rest_framework import status
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


class PaymentCallbackAPIView(APIView):

    def get(self, request):

        authority = request.query_params.get(
            "Authority"
        )

        payment_status = request.query_params.get(
            "Status"
        )

        if not authority:

            return Response(
                {
                    "detail": "Authority ارسال نشده است."
                },
                status=status.HTTP_400_BAD_REQUEST
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

            return Response(
                {
                    "detail": "پرداخت پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if payment.status == "success":

            return Response({
                "detail": "این پرداخت قبلاً تایید شده است.",
                "ref_id": payment.ref_id,
            })

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

            return Response({
                "detail": "پرداخت توسط کاربر لغو یا ناموفق شد."
            })

        gateway = ZarinpalService()

        try:

            result = gateway.verify_payment(
                authority=authority,
                amount=payment.amount,
            )

        except Exception:

            return Response(
                {
                    "detail": "خطا در تایید پرداخت."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        data = result.get("data", {})

        code = data.get("code")

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

            return Response({
                "detail": "پرداخت تایید نشد."
            })

        ref_id = data.get("ref_id")

        try:

            payment.ref_id = ref_id

            payment.save(
                update_fields=[
                    "ref_id",
                    "updated_at",
                ]
            )

            order, completed = complete_payment(
                payment_id=payment.id,
                request=request,
            )

        except ValueError as error:

            return Response(
                {
                    "detail": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST
            )