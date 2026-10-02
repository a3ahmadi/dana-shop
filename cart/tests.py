import json

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Color, Product


class CartPageTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="دفتر", slug="notebooks")
        self.black = Color.objects.create(name="مشکی")
        self.blue = Color.objects.create(name="آبی")
        self.product = Product.objects.create(
            category=category, name="دفتر آزمایشی", slug="sample-notebook",
            price=100000, discount_percent=10, stock=5, sku="CART-1",
        )
        self.product.colors.add(self.black, self.blue)
        self.page_url = reverse("storefront:cart")

    def add(self, color, quantity):
        return self.client.post(
            "/api/v1/cart/items/",
            data=json.dumps({"product_id": self.product.id, "color_id": color.id, "quantity": quantity}),
            content_type="application/json",
        )

    def test_empty_cart_page(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "سبد خرید شما خالی است")
        self.assertContains(response, 'id="cartTotal"')

    def test_page_uses_session_items_and_actual_totals(self):
        self.assertEqual(self.add(self.black, 2).status_code, 201)
        self.assertEqual(self.add(self.blue, 1).status_code, 201)
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["cart_items"]), 2)
        self.assertContains(response, self.product.name)
        self.assertContains(response, 'data-color-id="%s"' % self.black.id)
        self.assertContains(response, 'data-color-id="%s"' % self.blue.id)
        self.assertEqual(response.context["cart_count"], 3)
        self.assertEqual(response.context["cart_original_price"], 300000)
        self.assertEqual(response.context["cart_discount"], 30000)
        self.assertEqual(response.context["cart_total"], 270000)

    def test_update_and_delete_target_one_color(self):
        self.add(self.black, 2)
        self.add(self.blue, 1)
        url = "/api/v1/cart/items/%s/" % self.product.id
        response = self.client.patch(
            url, data=json.dumps({"color_id": self.black.id, "quantity": 3}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        cart = self.client.get("/api/v1/cart/").json()
        self.assertEqual({item["color_id"]: item["quantity"] for item in cart["items"]},
                         {self.black.id: 3, self.blue.id: 1})
        response = self.client.delete("/api/v1/cart/items/%s/delete/?color_id=%s" % (self.product.id, self.black.id))
        self.assertEqual(response.status_code, 200)
        cart = self.client.get("/api/v1/cart/").json()
        self.assertEqual([(item["color_id"], item["quantity"]) for item in cart["items"]], [(self.blue.id, 1)])

    def test_update_validates_color_and_stock(self):
        self.add(self.black, 1)
        url = "/api/v1/cart/items/%s/" % self.product.id
        missing_color = self.client.patch(url, data=json.dumps({"quantity": 2}), content_type="application/json")
        self.assertEqual(missing_color.status_code, 400)
        too_many = self.client.patch(
            url, data=json.dumps({"color_id": self.black.id, "quantity": 6}),
            content_type="application/json",
        )
        self.assertEqual(too_many.status_code, 400)
        self.assertEqual(self.client.get("/api/v1/cart/").json()["items"][0]["quantity"], 1)