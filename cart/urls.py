from django.urls import path

from .views import (
    CartView,
    CartAddItemView,
    CartUpdateItemView,
    CartDeleteItemView,
    CartClearView,
)


urlpatterns = [

    path(
        "",
        CartView.as_view(),
        name="cart"
    ),

    path(
        "items/",
        CartAddItemView.as_view(),
        name="cart-add"
    ),

    path(
        "items/<int:product_id>/",
        CartUpdateItemView.as_view(),
        name="cart-update"
    ),

    path(
        "items/<int:product_id>/delete/",
        CartDeleteItemView.as_view(),
        name="cart-delete"
    ),

    path(
        "clear/",
        CartClearView.as_view(),
        name="cart-clear"
    ),
]