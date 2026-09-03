from django.urls import path

from .views import CheckoutAPIView


urlpatterns = [
    path(
        "",
        CheckoutAPIView.as_view(),
        name="checkout"
    ),
]