from django.urls import path

from .views import CreateOrderAPIView


urlpatterns = [
    path(
        "create/",
        CreateOrderAPIView.as_view(),
        name="create-order"
    ),
]