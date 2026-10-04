import json

from django.conf import settings
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from orders.models import Order, OrderItem
from products.models import Category, Color, Product


class ProductDetailPageTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="لوازم", slug="stationery")
        self.color = Color.objects.create(name="آبی", hex_code="#0000ff")
        self.product = Product.objects.create(
            category=self.category,
            name="دفتر نمونه",
            slug="sample-notebook",
            description="توضیحات دفتر",
            price=100000,
            discount_percent=10,
            stock=5,
            sku="NOTE-1",
        )
        self.product.colors.add(self.color)

    def test_renders_product_data_and_purchase_form(self):
        response = self.client.get(reverse("storefront:product_detail", kwargs={"slug": self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)
        self.assertContains(response, self.color.name)
        self.assertContains(response, 'id="addToCartForm"')
        self.assertContains(response, "90,000")

    def test_inactive_product_is_not_public(self):
        self.product.is_active = False
        self.product.save()
        response = self.client.get(reverse("storefront:product_detail", kwargs={"slug": self.product.slug}))
        self.assertEqual(response.status_code, 404)

class HomePageTests(TestCase):
    def test_home_mounts_real_catalog_sections(self):
        response = self.client.get(reverse("storefront:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="homeCategoriesSlides"')
        self.assertContains(response, 'id="homeLatestSlides"')
        self.assertContains(response, 'id="catalogSearchInput"')
        self.assertContains(response, '<form id="catalogSearchForm" method="get" action="/products/"')
        self.assertContains(response, 'name="search"')
        self.assertNotContains(response, "Galaxy Tab S8")

    def test_catalog_api_exposes_fields_used_by_home(self):
        category = Category.objects.create(name="دفتر", slug="notebooks")
        Product.objects.create(
            category=category, name="دفتر خط‌دار", slug="lined-notebook",
            price=20000, discount_percent=5, stock=3, sku="NOTE-2",
        )
        categories = self.client.get("/api/v1/categories/?limit=100")
        products = self.client.get("/api/v1/products/?ordering=-created_at")
        self.assertEqual(categories.status_code, 200)
        self.assertEqual(products.status_code, 200)
        search = self.client.get("/api/v1/products/", {"search": "دفتر"})
        self.assertEqual(search.status_code, 200)
        self.assertEqual(search.json()[0]["name"], "دفتر خط‌دار")
        self.assertEqual(categories.json()["results"][0]["name"], category.name)
        item = products.json()[0]
        for field in ("name", "slug", "category", "price", "final_price", "discount_percent", "stock", "main_image"):
            self.assertIn(field, item)


class UserPanelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("09123456789")
        self.other_user = User.objects.create_user("09123456780")
        category = Category.objects.create(name="نوشت‌افزار", slug="panel-stationery")
        product = Product.objects.create(
            category=category, name="دفتر آزمون", slug="panel-notebook",
            price=100000, stock=5, sku="PANEL-1",
        )
        color = Color.objects.create(name="قرمز")
        product.colors.add(color)
        self.order = Order.objects.create(
            user=self.user, order_number="ORD-PANEL-1", recipient_name="گیرنده",
            phone="09123456789", state="تهران", city="تهران", postal_code="1234567890",
            complete_address="خیابان نمونه", shipping_method="courier",
            tracking_code="TIPAX-123", original_price=200000, total_price=200000,
            status="processing", payment_status="paid",
        )
        OrderItem.objects.create(
            order=self.order, product=product, product_name=product.name,
            color=color.name, price=100000, quantity=2, total_price=200000,
        )

    def test_panel_and_detail_redirect_anonymous_visitors_home(self):
        for url in (
            reverse("storefront:panel"),
            reverse("storefront:panel_order_detail", args=[self.order.id]),
            reverse("storefront:panel_order_detail", args=[self.order.id]) + "?fragment=1",
        ):
            self.assertRedirects(self.client.get(url), reverse("storefront:home"))

    def test_panel_has_two_tabs_real_orders_and_no_removed_account_fields(self):
        self.client.force_login(self.user)
        profile = self.user.profile
        profile.first_name = "علی"
        profile.last_name = "رضایی"
        profile.save()
        response = self.client.get(reverse("storefront:panel"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode().count("data-panel-tab="), 2)
        self.assertContains(response, 'name="first_name"')
        self.assertContains(response, 'name="last_name"')
        self.assertNotContains(response, 'name="email"')
        self.assertNotContains(response, 'name="phone"')
        self.assertNotContains(response, "تنظیمات امنیتی")
        self.assertNotContains(response, "تنظیمات حساب")
        self.assertContains(response, self.order.order_number)
        self.assertContains(response, self.order.tracking_code)
        self.assertContains(response, 'data-status="processing"')
        self.assertRegex(response.content.decode(), r'data-created="\d+"')
        self.assertContains(response, 'id="panelOrderStatus"')
        self.assertContains(response, 'id="panelOrderPeriod"')
        self.assertContains(response, 'id="panelOrderSearch"')
        self.assertContains(response, 'data-cancel-order="%s"' % self.order.id)
        self.assertContains(response, 'storefront/js/user-panel.js')
        self.order.tracking_code = ""
        self.order.save(update_fields=["tracking_code"])
        self.assertContains(self.client.get(reverse("storefront:panel")), "هنوز ثبت نشده")

    def test_order_detail_stays_in_orders_tab_and_is_private(self):
        self.client.force_login(self.user)
        url = reverse("storefront:panel_order_detail", args=[self.order.id])
        full = self.client.get(url)
        fragment = self.client.get(url + "?fragment=1")
        self.assertEqual(full.status_code, 200)
        self.assertEqual(full.context["selected_tab"], "orders")
        self.assertContains(full, self.order.order_number)
        self.assertContains(full, "دفتر آزمون")
        self.assertContains(full, self.order.tracking_code)
        self.assertNotContains(full, "روند سفارش")
        self.assertNotContains(full, "عملیات سفارش")
        self.assertTemplateUsed(fragment, "storefront/pages/user-panel-order-detail.html")
        self.assertContains(fragment, 'id="orderDetailContent"')
        self.assertNotContains(fragment, "<html")
        self.client.force_login(self.other_user)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.get(url + "?fragment=1").status_code, 404)

    def test_profile_saves_without_exposing_or_changing_email_or_phone(self):
        browser = Client(enforce_csrf_checks=True)
        browser.force_login(self.user)
        browser.get(reverse("storefront:panel"))
        csrf = browser.cookies[settings.CSRF_COOKIE_NAME].value
        response = browser.patch(
            reverse("accounts:profile"),
            data=json.dumps({"first_name": "سارا", "last_name": "رضایی", "birth": "۱۳۷۰/۰۵/۱۵", "gender": "woman", "email": "ignored@example.com", "phone": "09121111111"}),
            content_type="application/json", HTTP_X_CSRFTOKEN=csrf,
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("email", response.json())
        self.assertNotIn("phone", response.json())
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.phone_number, "09123456789")
        self.assertEqual(self.user.profile.email, "")
        self.assertEqual(self.user.profile.first_name, "سارا")

    def test_logout_is_post_only_and_returns_home(self):
        browser = Client(enforce_csrf_checks=True)
        browser.force_login(self.user)
        browser.get(reverse("storefront:panel"))
        self.assertEqual(browser.get(reverse("storefront:panel_logout")).status_code, 405)
        csrf = browser.cookies[settings.CSRF_COOKIE_NAME].value
        self.assertRedirects(
            browser.post(reverse("storefront:panel_logout"), HTTP_X_CSRFTOKEN=csrf),
            reverse("storefront:home"),
        )
        self.assertRedirects(browser.get(reverse("storefront:panel")), reverse("storefront:home"))
