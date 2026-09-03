from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from products.models import Product

from .cart import Cart
from .serializers import (
    AddToCartSerializer,
    UpdateCartItemSerializer,
    CartItemSerializer,
)


class CartView(APIView):

    def get(self, request):

        cart = Cart(request)

        items = list(cart)

        serializer = CartItemSerializer(
            items,
            many=True
        )

        return Response({
            "items": serializer.data,
            "total_items": cart.count(),
            "total_original_price": cart.total_original_price(),
            "total_discount": cart.total_discount(),
            "total_price": cart.total(),
        })


class CartAddItemView(APIView):

    def post(self, request):

        serializer = AddToCartSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        product_id = serializer.validated_data[
            "product_id"
        ]

        quantity = serializer.validated_data[
            "quantity"
        ]

        product = Product.objects.filter(
            id=product_id,
            is_active=True
        ).first()

        if not product:

            return Response(
                {
                    "detail": "محصول پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if product.stock < quantity:

            return Response(
                {
                    "detail": "موجودی محصول کافی نیست."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = Cart(request)

        try:

            cart.add(
                product=product,
                quantity=quantity
            )

        except ValueError as error:

            return Response(
                {
                    "detail": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "محصول به سبد خرید اضافه شد."
            },
            status=status.HTTP_201_CREATED
        )


class CartUpdateItemView(APIView):

    def patch(self, request, product_id):

        serializer = UpdateCartItemSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        quantity = serializer.validated_data[
            "quantity"
        ]

        cart = Cart(request)

        try:

            cart.update(
                product_id=product_id,
                quantity=quantity
            )

        except KeyError:

            return Response(
                {
                    "detail": "محصول در سبد خرید وجود ندارد."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError as error:

            return Response(
                {
                    "detail": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "تعداد محصول تغییر کرد."
            }
        )


class CartDeleteItemView(APIView):

    def delete(self, request, product_id):

        cart = Cart(request)

        if str(product_id) not in cart.cart:

            return Response(
                {
                    "detail": "محصول در سبد خرید وجود ندارد."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        cart.delete(product_id)

        return Response(
            {
                "message": "محصول از سبد خرید حذف شد."
            }
        )


class CartClearView(APIView):

    def delete(self, request):

        cart = Cart(request)

        cart.clear()

        return Response(
            {
                "message": "سبد خرید خالی شد."
            }
        )


