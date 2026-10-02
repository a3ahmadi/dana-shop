from django.test import TestCase
from django.urls import reverse

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