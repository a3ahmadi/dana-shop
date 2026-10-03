import json

from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from addresses.models import Address
from orders.models import Order
from products.models import Category, Color, Product


class CheckoutStageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="09123456789")
        self.other_user = User.objects.create_user(phone_number="09123456780")
        category = Category.objects.create(name="لوازم", slug="supplies")
        color = Color.objects.create(name="آبی")
        self.product = Product.objects.create(
            category=category, name="دفتر تست", slug="checkout-notebook",
            price=100000, discount_percent=10, stock=5, sku="CHECKOUT-1",
        )
        self.product.colors.add(color)
        self.color = color
        self.tehran = self.address("خانه", "تهران")
        self.tehran.is_default = True
        self.tehran.save()
        self.shiraz = self.address("محل کار", "شیراز")

    def address(self, title, city, user=None):
        return Address.objects.create(
            user=user or self.user, title=title, recipient_name="گیرنده تست",
            phone="09123456789", state="تهران" if city == "تهران" else "فارس",
            city=city, postal_code="1234567890", complete_address="خیابان نمونه",
        )

    def add_to_cart(self):
        return self.client.post(
            "/api/v1/cart/items/",
            data=json.dumps({"product_id": self.product.id, "color_id": self.color.id, "quantity": 2}),
            content_type="application/json",
        )

    def post_checkout(self, address, shipping="courier", payment="online"):
        return self.client.post(
            "/api/v1/checkout/",
            data=json.dumps({"address_id": address.id, "shipping_method": shipping, "payment_method": payment}),
            content_type="application/json",
        )

    def test_page_requires_login_and_cart(self):
        self.add_to_cart()
        response = self.client.get(reverse("storefront:checkout"))
        self.assertRedirects(response, "/login/?next=/checkout/", fetch_redirect_response=False)
        self.client.force_login(self.user)
        self.client.delete("/api/v1/cart/clear/")
        self.assertRedirects(self.client.get(reverse("storefront:checkout")), reverse("storefront:cart"))

    def test_page_uses_profile_cart_and_default_address(self):
        self.add_to_cart()
        self.client.force_login(self.user)
        response = self.client.get(reverse("storefront:checkout"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_address"], self.tehran)
        self.assertEqual(response.context["shipping_method"], "courier")
        self.assertEqual(response.context["cart_count"], 2)
        self.assertEqual(response.context["cart_total"], 180000)
        self.assertContains(response, self.product.name)
        self.assertContains(response, 'id="addressModal"')
        self.assertContains(response, "اسنپ‌پی")
        self.assertNotContains(response, 'type="email"')
        self.assertNotContains(response, "زمان تحویل")

    def test_modal_address_api_and_profile_can_be_saved(self):
        self.add_to_cart()
        self.client.force_login(self.user)
        profile_response = self.client.patch(
            "/api/v1/accounts/profile/",
            data=json.dumps({"first_name": "علی", "last_name": "رضایی"}),
            content_type="application/json",
        )
        self.assertEqual(profile_response.status_code, 200)
        address_response = self.client.post(
            "/api/v1/addresses/",
            data=json.dumps({
                "title": "جدید", "recipient_name": "علی رضایی", "phone": "09123456789",
                "state": "اصفهان", "city": "اصفهان", "postal_code": "1234567890",
                "complete_address": "خیابان نمونه", "is_default": False,
            }),
            content_type="application/json",
        )
        self.assertEqual(address_response.status_code, 201)
        self.assertEqual(address_response.json()["city"], "اصفهان")

    def test_authenticated_checkout_uses_csrf_token_from_page(self):
        browser = Client(enforce_csrf_checks=True)
        browser.force_login(self.user)
        session = browser.session
        session["cart"] = {
            f"{self.product.id}:{self.color.id}": {
                "product_id": self.product.id, "color_id": self.color.id, "quantity": 1,
            }
        }
        session.save()
        page = browser.get(reverse("storefront:checkout"))
        self.assertEqual(page.status_code, 200)
        token = browser.cookies["csrftoken"].value
        response = browser.patch(
            "/api/v1/accounts/profile/",
            data=json.dumps({"first_name": "علی", "last_name": "رضایی"}),
            content_type="application/json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)
        response = browser.post(
            "/api/v1/checkout/",
            data=json.dumps({"address_id": self.tehran.id, "shipping_method": "courier", "payment_method": "online"}),
            content_type="application/json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)

    def test_checkout_validates_profile_address_city_and_payment_without_order(self):
        self.add_to_cart()
        self.client.force_login(self.user)
        self.assertEqual(self.post_checkout(self.tehran).status_code, 400)
        profile = self.user.profile
        profile.first_name = "علی"
        profile.last_name = "رضایی"
        profile.save()
        foreign = self.address("دیگری", "تهران", user=self.other_user)
        self.assertEqual(self.post_checkout(foreign).status_code, 400)
        self.assertEqual(self.post_checkout(self.shiraz, "courier").status_code, 400)
        self.assertEqual(self.post_checkout(self.tehran, "tipax").status_code, 200)
        self.assertEqual(self.post_checkout(self.tehran, "courier", "snappay").status_code, 400)
        response = self.post_checkout(self.shiraz, "tipax")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["price"]["shipping_price"])
        self.assertEqual(self.client.session["checkout"], {
            "address_id": self.shiraz.id,
            "shipping_method": "tipax",
            "payment_method": "online",
        })
        self.assertEqual(Order.objects.count(), 0)
        page = self.client.get(reverse("storefront:checkout"))
        self.assertEqual(page.context["selected_address"], self.shiraz)
        self.assertEqual(page.context["shipping_method"], "tipax")
