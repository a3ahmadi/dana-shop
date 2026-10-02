from django.urls import path

from . import views


app_name = "storefront"


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("products/", views.ProductListPageView.as_view(), name="products"),
    path("cart/", views.CartPageView.as_view(), name="cart"),
    path("products/<str:slug>/", views.ProductDetailPageView.as_view(), name="product_detail"),
]