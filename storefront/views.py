from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "storefront/pages/home.html"

class LoginView(TemplateView):
    template_name = "storefront/pages/login.html"

class ProductListPageView(TemplateView):
    template_name = "storefront/pages/products.html"