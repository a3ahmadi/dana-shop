import uuid
from collections import defaultdict
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from addresses.models import Address
from cart.cart import Cart
from products.models import Product
from .models import Order, OrderItem
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    CreateOrderSerializer,
    CancelOrderSerializer,
    UpdateOrderStatusSerializer,
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

        quantities = defaultdict(int)
        for item in items:
            quantities[item["product"].id] += item["quantity"]
        products = Product.objects.select_for_update().in_bulk(quantities)
        for product_id, quantity in quantities.items():
            product = products.get(product_id)
            if not product or not product.is_active or product.stock < quantity:
                return Response(
                    {"detail": "موجودی یکی از محصولات سبد خرید کافی نیست. سبد را بررسی کنید."},
                    status=status.HTTP_400_BAD_REQUEST,
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

        # آیتم‌های سفارش در انتظار پرداخت را با سبد فعلی همگام کن.
        existing_items = {
            (item.product_id, item.color): item
            for item in order.items.select_for_update()
        }
        new_items = []
        changed_items = []

        for item in items:

            product = item["product"]
            color = item["color"]
            order_item = existing_items.pop((product.id, color.name), None)
            if order_item is None:
                new_items.append(OrderItem(
                    order=order,
                    product=product,
                    product_name=product.name,
                    color=color.name,
                    price=item["final_price"],
                    quantity=item["quantity"],
                    total_price=item["total"],
                ))
            else:
                order_item.product_name = product.name
                order_item.price = item["final_price"]
                order_item.quantity = item["quantity"]
                order_item.total_price = item["total"]
                changed_items.append(order_item)

        if existing_items:
            OrderItem.objects.filter(id__in=[item.id for item in existing_items.values()]).delete()
        if changed_items:
            OrderItem.objects.bulk_update(changed_items, ["product_name", "price", "quantity", "total_price"])
        if new_items:
            OrderItem.objects.bulk_create(new_items)

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

        if order.status == "processing" and order.payment_status == "paid":
            quantities = defaultdict(int)
            for item in order.items.all():
                quantities[item.product_id] += item.quantity
            products = Product.objects.select_for_update().in_bulk(quantities)
            for product_id, quantity in quantities.items():
                product = products[product_id]
                product.stock += quantity
                product.save(update_fields=["stock", "updated_at"])

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


class UpdateOrderStatusAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

    @transaction.atomic
    def patch(self, request, id):

        order = (
            Order.objects
            .select_for_update()
            .filter(id=id)
            .first()
        )

        if not order:
            return Response(
                {
                    "detail": "سفارش پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UpdateOrderStatusSerializer(
            data=request.data,
            context={
                "order": order
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        new_status = serializer.validated_data[
            "status"
        ]

        order.status = new_status

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": "وضعیت سفارش با موفقیت تغییر کرد.",
                "order": {
                    "id": order.id,
                    "order_number": order.order_number,
                    "status": order.status,
                    "payment_status": order.payment_status,
                }
            },
            status=status.HTTP_200_OK
        )
