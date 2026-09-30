from django.db import models
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from core.pagination import LimitOffsetPaginations
from .filters import ProductFilter
from .models import Category, Color, Product
from .serializers import (
    CategorySerializer,
    ColorSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
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


class ColorListAPIView(ListAPIView):
    serializer_class = ColorSerializer
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPaginations
    queryset = Color.objects.filter(is_active=True)


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPaginations

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
        return (
            Product.objects
            .filter(is_active=True)
            .select_related("category")
            .prefetch_related("colors")
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
            "colors",
        )
    )
