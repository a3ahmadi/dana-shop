from django.urls import path

from .views import CreatePaymentAPIView, PaymentCallbackAPIView


urlpatterns = [

    path(
        "create/",
        CreatePaymentAPIView.as_view(),
        name="create-payment"
    ),

    path(
        "callback/",
        PaymentCallbackAPIView.as_view(),
        name="payment-callback"
    ),

]