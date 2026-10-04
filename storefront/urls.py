from django.urls import path

from . import views


app_name = "storefront"


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("products/", views.ProductListPageView.as_view(), name="products"),
    path("cart/", views.CartPageView.as_view(), name="cart"),
    path("checkout/", views.CheckoutPageView.as_view(), name="checkout"),
    path("accept/", views.AcceptPageView.as_view(), name="accept"),
    path("panel/", views.UserPanelPageView.as_view(), name="panel"),
    path("panel/orders/<int:order_id>/", views.UserPanelOrderDetailView.as_view(), name="panel_order_detail"),
    path("panel/logout/", views.UserPanelLogoutView.as_view(), name="panel_logout"),
    path("products/<str:slug>/", views.ProductDetailPageView.as_view(), name="product_detail"),
]
