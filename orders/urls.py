from django.urls import path

from .views import (
    CreateOrderAPIView,
    OrderListAPIView,
    OrderDetailAPIView,
    CancelOrderAPIView,
    UpdateOrderStatusAPIView,
)


urlpatterns = [

    path(
        "create/",
        CreateOrderAPIView.as_view(),
        name="create-order"
    ),

    path(
        "",
        OrderListAPIView.as_view(),
        name="order-list"
    ),

    path(
        "<int:id>/",
        OrderDetailAPIView.as_view(),
        name="order-detail"
    ),
    path(
        "<int:id>/cancel/",
        CancelOrderAPIView.as_view(),
        name="cancel-order"
    ),
    path(
        "<int:id>/status/",
        UpdateOrderStatusAPIView.as_view(),
        name="update-order-status"
    ),

]