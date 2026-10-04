import json
from unittest.mock import patch

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from addresses.models import Address
from orders.models import Order, OrderItem
from payment.models import Payment
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
            "cart_signature": [[self.product.id, self.color.id, 2, "90000"]],
        })
        self.assertEqual(Order.objects.count(), 0)
        page = self.client.get(reverse("storefront:checkout"))
        self.assertEqual(page.context["selected_address"], self.shiraz)
        self.assertEqual(page.context["shipping_method"], "tipax")

    def prepare_confirmation(self, address=None, shipping="courier"):
        self.add_to_cart()
        self.client.force_login(self.user)
        profile = self.user.profile
        profile.first_name = "علی"
        profile.last_name = "رضایی"
        profile.save()
        response = self.post_checkout(address or self.tehran, shipping)
        self.assertEqual(response.status_code, 200)

    def test_confirmation_requires_saved_selection_and_shows_real_details(self):
        self.add_to_cart()
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(reverse("storefront:accept")), reverse("storefront:checkout"))
        profile = self.user.profile
        profile.first_name = "علی"
        profile.last_name = "رضایی"
        profile.save()
        self.assertEqual(self.post_checkout(self.shiraz, "tipax").status_code, 200)
        response = self.client.get(reverse("storefront:accept"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["address"], self.shiraz)
        self.assertEqual(response.context["shipping_method"], "tipax")
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.shiraz.complete_address)
        self.assertContains(response, "پس‌کرایه")
        self.assertContains(response, 'href="/checkout/"')
        self.assertEqual(Order.objects.count(), 0)

    def test_confirmation_rechecks_deleted_address(self):
        self.prepare_confirmation()
        self.tehran.delete()
        self.assertRedirects(self.client.get(reverse("storefront:accept")), reverse("storefront:checkout"))
        response = self.client.post(
            "/api/v1/orders/create/",
            data=json.dumps({"address_id": self.shiraz.id, "shipping_method": "tipax"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_cart_change_requires_checkout_again_before_order_creation(self):
        self.prepare_confirmation()
        self.client.patch(
            f"/api/v1/cart/items/{self.product.id}/",
            data=json.dumps({"color_id": self.color.id, "quantity": 3}),
            content_type="application/json",
        )
        self.assertRedirects(self.client.get(reverse("storefront:accept")), reverse("storefront:checkout"))
        response = self.client.post(
            "/api/v1/orders/create/",
            data=json.dumps({"address_id": self.tehran.id, "shipping_method": "courier"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_confirmation_creates_pending_order_only_on_explicit_action(self):
        self.prepare_confirmation()
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(self.client.get(reverse("storefront:accept")).status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        response = self.client.post(
            "/api/v1/orders/create/",
            data=json.dumps({"address_id": self.tehran.id, "shipping_method": "courier"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.id, response.json()["order"]["id"])
        self.assertEqual(order.total_price, 180000)
        self.assertEqual(order.shipping_price, 0)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.status, "pending")

        with override_settings(ZARINPAL_MERCHANT_ID=None, ZARINPAL_CALLBACK_URL=None):
            unconfigured = self.client.post(
                "/api/v1/payments/create/",
                data=json.dumps({"order_id": order.id}), content_type="application/json",
            )
        self.assertEqual(unconfigured.status_code, 503)
        self.assertEqual(Payment.objects.count(), 0)

        with override_settings(ZARINPAL_MERCHANT_ID="test-merchant", ZARINPAL_CALLBACK_URL="https://example.test/callback"):
            with patch("payment.views.ZarinpalService.request_payment", return_value="https://www.zarinpal.com/pg/StartPay/TEST"):
                payment_response = self.client.post(
                    "/api/v1/payments/create/",
                    data=json.dumps({"order_id": order.id}), content_type="application/json",
                )
        self.assertEqual(payment_response.status_code, 201)
        self.assertEqual(payment_response.json()["payment"]["payment_url"], "https://www.zarinpal.com/pg/StartPay/TEST")

    def test_returning_to_cart_updates_items_on_the_same_pending_order(self):
        self.prepare_confirmation()
        order_url = "/api/v1/orders/create/"
        payload = json.dumps({"address_id": self.tehran.id, "shipping_method": "courier"})
        self.assertEqual(self.client.post(order_url, payload, content_type="application/json").status_code, 200)
        order = Order.objects.get(user=self.user)
        order_number = order.order_number
        original_item = order.items.get()

        second_color = Color.objects.create(name="سبز")
        self.product.colors.add(second_color)
        self.assertEqual(self.client.patch(
            f"/api/v1/cart/items/{self.product.id}/",
            data=json.dumps({"color_id": self.color.id, "quantity": 1}),
            content_type="application/json",
        ).status_code, 200)
        self.assertEqual(self.client.post(
            "/api/v1/cart/items/",
            data=json.dumps({"product_id": self.product.id, "color_id": second_color.id, "quantity": 2}),
            content_type="application/json",
        ).status_code, 201)
        self.assertEqual(self.post_checkout(self.shiraz, "tipax").status_code, 200)
        response = self.client.post(
            order_url,
            data=json.dumps({"address_id": self.shiraz.id, "shipping_method": "tipax"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        self.assertEqual(response.json()["order"]["id"], order.id)
        self.assertEqual(order.order_number, order_number)
        self.assertEqual(order.shipping_method, "tipax")
        self.assertEqual(order.city, "شیراز")
        self.assertEqual(order.total_price, 270000)
        self.assertEqual(order.items.count(), 2)
        original_item.refresh_from_db()
        self.assertEqual(original_item.quantity, 1)
        self.assertEqual(original_item.total_price, 90000)
        added_item = order.items.get(color=second_color.name)
        self.assertEqual(added_item.quantity, 2)

        self.assertEqual(self.client.delete(
            f"/api/v1/cart/items/{self.product.id}/delete/?color_id={self.color.id}"
        ).status_code, 200)
        self.assertEqual(self.post_checkout(self.shiraz, "tipax").status_code, 200)
        self.assertEqual(self.client.post(
            order_url,
            data=json.dumps({"address_id": self.shiraz.id, "shipping_method": "tipax"}),
            content_type="application/json",
        ).status_code, 200)
        order.refresh_from_db()
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        self.assertEqual(order.items.count(), 1)
        self.assertFalse(OrderItem.objects.filter(id=original_item.id).exists())
        self.assertEqual(order.items.get().id, added_item.id)
        self.assertEqual(order.total_price, 180000)

    def test_order_items_are_visible_in_admin(self):
        self.prepare_confirmation()
        self.client.post(
            "/api/v1/orders/create/",
            data=json.dumps({"address_id": self.tehran.id, "shipping_method": "courier"}),
            content_type="application/json",
        )
        order = Order.objects.get(user=self.user)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save(update_fields=["is_staff", "is_superuser"])

        response = self.client.get(reverse("admin:orders_order_change", args=[order.id]))
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.color.name)
        self.assertEqual(self.client.get(reverse("admin:orders_orderitem_changelist")).status_code, 200)

    def test_order_creation_checks_combined_stock_for_two_colors(self):
        second_color = Color.objects.create(name="سبز")
        self.product.colors.add(second_color)
        self.add_to_cart()
        self.client.post(
            "/api/v1/cart/items/",
            data=json.dumps({"product_id": self.product.id, "color_id": second_color.id, "quantity": 4}),
            content_type="application/json",
        )
        self.client.force_login(self.user)
        profile = self.user.profile
        profile.first_name = "علی"
        profile.last_name = "رضایی"
        profile.save()
        self.assertEqual(self.post_checkout(self.tehran).status_code, 200)
        response = self.client.post(
            "/api/v1/orders/create/",
            data=json.dumps({"address_id": self.tehran.id, "shipping_method": "courier"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_successful_payment_callback_returns_result(self):
        self.prepare_confirmation()
        self.client.post(
            "/api/v1/orders/create/",
            data=json.dumps({"address_id": self.tehran.id, "shipping_method": "courier"}),
            content_type="application/json",
        )
        order = Order.objects.get(user=self.user)
        payment = Payment.objects.create(order=order, amount=order.total_price, authority="TEST-AUTHORITY")
        with patch("payment.views.ZarinpalService.verify_payment", return_value={"data": {"code": 100, "ref_id": "REF-1"}}):
            response = self.client.get("/api/v1/payments/callback/?Authority=TEST-AUTHORITY&Status=OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["order_number"], order.order_number)
        self.assertEqual(response.json()["ref_id"], "REF-1")
        order.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(order.status, "paid")
        self.assertEqual(payment.status, "success")

    def test_payment_callback_checks_combined_stock_after_checkout(self):
        second_color = Color.objects.create(name="سبز")
        self.product.colors.add(second_color)
        self.add_to_cart()
        self.client.post(
            "/api/v1/cart/items/",
            data=json.dumps({"product_id": self.product.id, "color_id": second_color.id, "quantity": 2}),
            content_type="application/json",
        )
        self.client.force_login(self.user)
        profile = self.user.profile
        profile.first_name = "علی"
        profile.last_name = "رضایی"
        profile.save()
        self.assertEqual(self.post_checkout(self.tehran).status_code, 200)
        response = self.client.post(
            "/api/v1/orders/create/",
            data=json.dumps({"address_id": self.tehran.id, "shipping_method": "courier"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        order = Order.objects.get(user=self.user)
        payment = Payment.objects.create(order=order, amount=order.total_price, authority="TEST-COMBINED")
        self.product.stock = 3
        self.product.save(update_fields=["stock"])

        with patch("payment.views.ZarinpalService.verify_payment", return_value={"data": {"code": 100, "ref_id": "REF-2"}}):
            callback = self.client.get("/api/v1/payments/callback/?Authority=TEST-COMBINED&Status=OK")

        self.assertEqual(callback.status_code, 400)
        self.product.refresh_from_db()
        order.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(order.status, "pending")
        self.assertNotEqual(payment.status, "success")
