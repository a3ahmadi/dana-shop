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