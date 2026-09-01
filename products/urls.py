from django.urls import path

from .views import (
    CategoryListAPIView,
    CategoryDetailAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
)


urlpatterns = [

    path(
        "categories/",
        CategoryListAPIView.as_view(),
        name="category-list",
    ),

    path(
        "categories/<slug:slug>/",
        CategoryDetailAPIView.as_view(),
        name="category-detail",
    ),

    path(
        "products/",
        ProductListAPIView.as_view(),
        name="product-list",
    ),

    path(
        "products/<slug:slug>/",
        ProductDetailAPIView.as_view(),
        name="product-detail",
    ),
]