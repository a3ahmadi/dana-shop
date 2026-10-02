from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from django.views.generic import DetailView, TemplateView

from accounts.redirects import safe_next_url
from cart.cart import Cart
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