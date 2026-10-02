from django.db.models import Prefetch
from django.views.generic import DetailView, TemplateView

from products.models import Color, Product


class HomeView(TemplateView):
    template_name = "storefront/pages/home.html"


class LoginView(TemplateView):
    template_name = "storefront/pages/login.html"


class ProductListPageView(TemplateView):
    template_name = "storefront/pages/products.html"


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