from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from django.views import View
from django.views.generic import DetailView, TemplateView

from accounts.redirects import safe_next_url
from addresses.models import Address
from cart.cart import Cart
from checkouts.serializers import CheckoutSerializer
from checkouts.state import cart_signature
from checkouts.validators import available_shipping_methods, shipping_for_city
from orders.models import Order
from products.models import Color, Product


class HomeView(TemplateView):
    template_name = "storefront/pages/home.html"


@method_decorator(never_cache, name="dispatch")
class LoginView(TemplateView):
    template_name = "storefront/pages/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(safe_next_url(request, request.GET.get("next")))
        return super().get(request, *args, **kwargs)


class ProductListPageView(TemplateView):
    template_name = "storefront/pages/products.html"


class CartPageView(TemplateView):
    template_name = "storefront/pages/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        items = list(cart)
        context.update({
            "cart_items": items,
            "cart_count": sum(item["quantity"] for item in items),
            "cart_original_price": sum(item["price"] * item["quantity"] for item in items),
            "cart_discount": sum((item["price"] - item["final_price"]) * item["quantity"] for item in items),
            "cart_total": sum(item["total"] for item in items),
        })
        return context


class CheckoutPageView(LoginRequiredMixin, TemplateView):
    template_name = "storefront/pages/checkout.html"

    def get(self, request, *args, **kwargs):
        if not list(Cart(request)):
            return redirect("storefront:cart")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = list(Cart(self.request))
        addresses = list(Address.objects.filter(user=self.request.user).order_by("-is_default", "-created_at"))
        saved = self.request.session.get("checkout", {})
        selected_address = next((address for address in addresses if address.id == saved.get("address_id")), None)
        if selected_address is None and addresses:
            selected_address = addresses[0]
        shipping_method = ""
        if selected_address:
            saved_method = saved.get("shipping_method") if saved.get("address_id") == selected_address.id else None
            shipping_method = (
                saved_method if saved_method in available_shipping_methods(selected_address.city)
                else shipping_for_city(selected_address.city)
            )
        context.update({
            "cart_items": items,
            "cart_count": sum(item["quantity"] for item in items),
            "cart_original_price": sum(item["price"] * item["quantity"] for item in items),
            "cart_discount": sum((item["price"] - item["final_price"]) * item["quantity"] for item in items),
            "cart_total": sum(item["total"] for item in items),
            "profile": self.request.user.profile,
            "addresses": addresses,
            "selected_address": selected_address,
            "shipping_method": shipping_method,
            "courier_available": bool(selected_address and "courier" in available_shipping_methods(selected_address.city)),
        })
        return context


class AcceptPageView(LoginRequiredMixin, TemplateView):
    template_name = "storefront/pages/accept.html"

    def get(self, request, *args, **kwargs):
        items = list(Cart(request))
        if not items:
            return redirect("storefront:cart")
        selected = request.session.get("checkout") or {}
        if selected.get("cart_signature") != cart_signature(items):
            return redirect("storefront:checkout")
        serializer = CheckoutSerializer(data=selected, context={"request": request})
        if not serializer.is_valid():
            return redirect("storefront:checkout")
        self.items = items
        self.address = Address.objects.get(id=selected["address_id"], user=request.user)
        self.shipping_method = selected["shipping_method"]
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "cart_items": self.items,
            "cart_count": sum(item["quantity"] for item in self.items),
            "cart_original_price": sum(item["price"] * item["quantity"] for item in self.items),
            "cart_discount": sum((item["price"] - item["final_price"]) * item["quantity"] for item in self.items),
            "cart_total": sum(item["total"] for item in self.items),
            "address": self.address,
            "shipping_method": self.shipping_method,
        })
        return context


class PanelAccessMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        return redirect("storefront:home")


@method_decorator(never_cache, name="dispatch")
class UserPanelPageView(PanelAccessMixin, TemplateView):
    template_name = "storefront/pages/user-panel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = list(
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items")
            .order_by("-created_at")
        )
        context.update({
            "profile": self.request.user.profile,
            "orders": orders,
            "active_orders_count": sum(order.status in ("pending", "paid", "processing", "shipping") for order in orders),
            "selected_tab": "orders" if self.request.GET.get("tab") == "orders" else "profile",
            "selected_order": getattr(self, "selected_order", None),
            "selected_payment": getattr(self, "selected_payment", None),
        })
        return context


@method_decorator(never_cache, name="dispatch")
class UserPanelOrderDetailView(UserPanelPageView):
    def get(self, request, order_id, *args, **kwargs):
        self.selected_order = get_object_or_404(
            Order.objects.select_related("payment").prefetch_related("items__product"),
            id=order_id,
            user=request.user,
        )
        self.selected_payment = getattr(self.selected_order, "payment", None)
        if request.GET.get("fragment") == "1":
            return render(request, "storefront/pages/user-panel-order-detail.html", {
                "order": self.selected_order,
                "payment": self.selected_payment,
            })
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_tab"] = "orders"
        return context


class UserPanelLogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("storefront:home")


class ProductDetailPageView(DetailView):
    template_name = "storefront/pages/product.html"
    context_object_name = "product"

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True, category__is_active=True)
            .select_related("category")
            .prefetch_related(
                "images",
                Prefetch(
                    "colors",
                    queryset=Color.objects.filter(is_active=True),
                    to_attr="available_colors",
                ),
            )
        )
