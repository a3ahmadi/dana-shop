import uuid
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from addresses.models import Address
from cart.cart import Cart
from .models import Order, OrderItem
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    CreateOrderSerializer,
    CancelOrderSerializer,
)


class CreateOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        cart = Cart(request)

        items = list(cart)

        if not items:
            return Response(
                {
                    "detail": "سبد خرید شما خالی است."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CreateOrderSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        address = Address.objects.get(
            id=serializer.validated_data["address_id"],
            user=request.user
        )

        shipping_method = serializer.validated_data[
            "shipping_method"
        ]

        original_price = cart.total()

        # پیدا کردن سفارش فعال کاربر
        order = (
            Order.objects
            .select_for_update()
            .filter(
                user=request.user,
                status="pending",
            )
            .first()
        )

        # اگر سفارش فعال وجود نداشت، ایجاد کن
        if not order:

            order_number = (
                f"ORD-{uuid.uuid4().hex[:10].upper()}"
            )

            order = Order.objects.create(
                user=request.user,
                order_number=order_number,

                recipient_name=address.recipient_name,
                phone=address.phone,
                state=address.state,
                city=address.city,
                postal_code=address.postal_code,
                complete_address=address.complete_address,

                shipping_method=shipping_method,
                shipping_price=0,

                original_price=original_price,
                total_price=original_price,

                status="pending",
                payment_status="unpaid",
            )

        # اگر سفارش قبلی وجود داشت، اطلاعاتش را آپدیت کن
        else:

            order.recipient_name = address.recipient_name
            order.phone = address.phone
            order.state = address.state
            order.city = address.city
            order.postal_code = address.postal_code
            order.complete_address = address.complete_address

            order.shipping_method = shipping_method
            order.shipping_price = 0

            order.original_price = original_price
            order.total_price = original_price

            order.save()

            # آیتم‌های قبلی سفارش را حذف کن
            order.items.all().delete()

        # ساخت آیتم‌های جدید
        order_items = []

        for item in items:

            product = item["product"]
            color = item["color"]
            quantity = item["quantity"]

            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    product_name=product.name,
                    color=color.name,
                    price=item["final_price"],
                    quantity=quantity,
                    total_price=item["total"],
                )
            )

        OrderItem.objects.bulk_create(
            order_items
        )

        return Response(
            {
                "detail": "سفارش با موفقیت ایجاد یا بروزرسانی شد.",

                "order": {
                    "id": order.id,
                    "order_number": order.order_number,
                    "status": order.status,
                    "payment_status": order.payment_status,

                    "shipping": {
                        "method": order.shipping_method,
                        "price": order.shipping_price,
                        "payment": "پس‌کرایه",
                    },

                    "price": {
                        "original_price": order.original_price,
                        "shipping_price": order.shipping_price,
                        "total_price": order.total_price,
                    },

                    "items": [
                        {
                            "product_id": item.product.id,
                            "product_name": item.product_name,
                            "color": item.color,
                            "price": item.price,
                            "quantity": item.quantity,
                            "total_price": item.total_price,
                        }
                        for item in order.items.all()
                    ],
                }
            },
            status=status.HTTP_200_OK
        )


class OrderListAPIView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = OrderListSerializer

    def get_queryset(self):

        return (
            Order.objects
            .filter(
                user=self.request.user
            )
            .order_by("-created_at")
        )


class OrderDetailAPIView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = OrderDetailSerializer

    lookup_field = "id"

    def get_queryset(self):

        return (
            Order.objects
            .filter(
                user=self.request.user
            )
            .prefetch_related("items")
        )


class CancelOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, id):

        order = (
            Order.objects
            .select_for_update()
            .filter(
                id=id,
                user=request.user
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

        serializer = CancelOrderSerializer(
            data={},
            context={
                "order": order
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        order.status = "cancelled"

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": "سفارش با موفقیت لغو شد.",
                "order": {
                    "id": order.id,
                    "order_number": order.order_number,
                    "status": order.status,
                    "payment_status": order.payment_status,
                }
            },
            status=status.HTTP_200_OK
        )