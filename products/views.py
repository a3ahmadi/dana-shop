from django.db.models import Count
from django.db import models
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import AllowAny
from core.pagination import CursorPaginations, LimitOffsetPaginations
from .models import (
    Category,
    Product,
)
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)


class CategoryListAPIView(ListAPIView):

    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPaginations

    queryset = (
        Category.objects
        .filter(is_active=True)
        .annotate(
            product_count=Count(
                "products",
                filter=models.Q(
                    products__is_active=True
                )
            )
        )
    )


class CategoryDetailAPIView(RetrieveAPIView):

    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    lookup_field = "slug"

    queryset = (
        Category.objects
        .filter(is_active=True)
        .annotate(
            product_count=Count(
                "products",
                filter=models.Q(
                    products__is_active=True
                )
            )
        )
    )


class ProductListAPIView(ListAPIView):

    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPaginations

    queryset = (
        Product.objects
        .filter(is_active=True)
        .select_related(
            "category"
        )
    )


class ProductDetailAPIView(RetrieveAPIView):

    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]

    lookup_field = "slug"

    queryset = (
        Product.objects
        .filter(is_active=True)
        .select_related(
            "category"
        )
        .prefetch_related(
            "images",
        )
    )


