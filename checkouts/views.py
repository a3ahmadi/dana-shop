from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from addresses.models import Address
from cart.cart import Cart

from .serializers import CheckoutSerializer
from .validators import SHIPPING_METHODS


class CheckoutAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        cart = Cart(request)

        items = list(cart)

        if not items:
            return Response(
                {
                    "detail": "سبد خرید شما خالی است."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        addresses = Address.objects.filter(
            user=request.user
        ).order_by(
            "-is_default",
            "-created_at"
        )

        cart_items = []

        for item in items:
            cart_items.append({
                "product_id": item["product"].id,
                "name": item["product"].name,
                "quantity": item["quantity"],
                "price": item["price"],
                "final_price": item["final_price"],
                "total": item["total"],
            })

        shipping_methods = [
            {
                "code": code,
                "title": title,
                "payment": "پس‌کرایه"
            }
            for code, title in SHIPPING_METHODS.items()
        ]

        return Response({

            "cart": {
                "items": cart_items,
                "total_items": cart.count(),
                "total_original_price": cart.total_original_price(),
                "total_discount": cart.total_discount(),
                "total_price": cart.total(),
            },

            "addresses": [
                {
                    "id": address.id,
                    "title": address.title,
                    "recipient_name": address.recipient_name,
                    "phone": address.phone,
                    "state": address.state,
                    "city": address.city,
                    "postal_code": address.postal_code,
                    "complete_address": address.complete_address,
                    "is_default": address.is_default,
                }
                for address in addresses
            ],

            "shipping_methods": shipping_methods,
        })

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

        serializer = CheckoutSerializer(
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

        products_price = cart.total()

        return Response(
            {
                "address": {
                    "id": address.id,
                    "title": address.title,
                    "recipient_name": address.recipient_name,
                    "phone": address.phone,
                    "state": address.state,
                    "city": address.city,
                    "postal_code": address.postal_code,
                    "complete_address": address.complete_address,
                },

                "shipping": {
                    "method": shipping_method,
                    "title": SHIPPING_METHODS[shipping_method],
                    "payment": "پس‌کرایه",
                },

                "price": {
                    "products_price": products_price,
                    "shipping_price": 0,
                    "total_price": products_price,
                }
            },
            status=status.HTTP_200_OK
        )