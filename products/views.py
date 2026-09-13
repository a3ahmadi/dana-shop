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
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from .filters import ProductFilter


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


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ProductFilter

    search_fields = [
        "name",
        "description",
        "sku",
    ]

    ordering_fields = [
        "price",
        "created_at",
        "name",
        "stock",
    ]

    ordering = [
        "-created_at"
    ]

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True
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


