from django.test import TestCase

from accounts.models import User
from orders.models import Order, OrderItem
from products.models import Category, Color, Product


class CustomerCancellationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("09123456789")
        self.other_user = User.objects.create_user("09123456780")
        category = Category.objects.create(name="نوشت‌افزار", slug="cancel-stationery")
        product = Product.objects.create(
            category=category, name="دفتر تست", slug="cancel-notebook",
            price=100000, stock=3, sku="CANCEL-1",
        )
        color = Color.objects.create(name="آبی")
        product.colors.add(color)
        self.product = product
        self.order = Order.objects.create(
            user=self.user, order_number="ORD-CANCEL-1", recipient_name="گیرنده",
            phone="09123456789", state="تهران", city="تهران", postal_code="1234567890",
            complete_address="خیابان نمونه", shipping_method="courier",
            original_price=200000, total_price=200000,
            status="processing", payment_status="paid",
        )
        OrderItem.objects.create(
            order=self.order, product=product, product_name=product.name,
            color=color.name, price=100000, quantity=2, total_price=200000,
        )

    def test_processing_order_can_be_cancelled_once_and_stock_is_restored(self):
        self.client.force_login(self.user)
        url = f"/api/v1/orders/{self.order.id}/cancel/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(self.client.post(url).status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_customer_cannot_cancel_another_users_or_shipped_order(self):
        url = f"/api/v1/orders/{self.order.id}/cancel/"
        self.client.force_login(self.other_user)
        self.assertEqual(self.client.post(url).status_code, 404)
        self.client.force_login(self.user)
        self.order.status = "shipping"
        self.order.save(update_fields=["status"])
        self.assertEqual(self.client.post(url).status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
