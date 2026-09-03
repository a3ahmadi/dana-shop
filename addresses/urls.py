from django.urls import path

from .views import (
    AddressListCreateAPIView,
    AddressDetailAPIView,
    AddressSetDefaultAPIView,
)


urlpatterns = [

    path(
        "",
        AddressListCreateAPIView.as_view(),
        name="address-list-create"
    ),

    path(
        "<int:pk>/",
        AddressDetailAPIView.as_view(),
        name="address-detail"
    ),

    path(
        "<int:pk>/set-default/",
        AddressSetDefaultAPIView.as_view(),
        name="address-set-default"
    ),
]