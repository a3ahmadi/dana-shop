from django.db import transaction
import requests
from django.conf import settings
from orders.models import Order
from .models import Payment


@transaction.atomic
def create_payment(order, user):

    if order.user != user:
        raise ValueError(
            "این سفارش متعلق به شما نیست."
        )

    if order.status != "pending":
        raise ValueError(
            "این سفارش در وضعیت قابل پرداخت نیست."
        )

    if order.payment_status == "paid":
        raise ValueError(
            "این سفارش قبلاً پرداخت شده است."
        )

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "amount": order.total_price,
            "status": "pending",
        }
    )

    if not created:

        payment.amount = order.total_price
        payment.status = "pending"

        payment.save(
            update_fields=[
                "amount",
                "status",
                "updated_at",
            ]
        )

    return payment


class ZarinpalService:

    REQUEST_URL = (
        "https://api.zarinpal.com/pg/v4/payment/request.json"
    )

    VERIFY_URL = (
        "https://api.zarinpal.com/pg/v4/payment/verify.json"
    )

    PAYMENT_URL = (
        "https://www.zarinpal.com/pg/StartPay/"
    )

    def request_payment(self, payment):

        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": payment.amount,
            "description": (
                f"پرداخت سفارش {payment.order.order_number}"
            ),
            "callback_url": (
                settings.ZARINPAL_CALLBACK_URL
            ),
            "metadata": {
                "order_id": str(payment.order.id),
            },
        }

        response = requests.post(
            self.REQUEST_URL,
            json=data,
            timeout=15,
        )

        response.raise_for_status()

        result = response.json()

        if result.get("errors"):
            raise ValueError(
                result["errors"].get(
                    "message",
                    "خطا در ایجاد تراکنش."
                )
            )

        payment_data = result.get("data", {})

        if payment_data.get("code") != 100:
            raise ValueError(
                "خطا در ایجاد تراکنش پرداخت."
            )

        authority = payment_data["authority"]

        payment.authority = authority
        payment.status = "pending"

        payment.save(
            update_fields=[
                "authority",
                "status",
                "updated_at",
            ]
        )

        return (
            f"{self.PAYMENT_URL}{authority}"
        )

    def verify_payment(
        self,
        authority,
        amount
    ):

        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "authority": authority,
            "amount": amount,
        }

        response = requests.post(
            self.VERIFY_URL,
            json=data,
            timeout=15,
        )

        response.raise_for_status()

        return response.json()