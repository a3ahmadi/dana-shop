from django.conf import settings
from django.db import models
from products.models import Color


class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("paid", "پرداخت شده"),
        ("processing", "در حال پردازش"),
        ("shipping", "ارسال شده"),
        ("delivered", "تحویل داده شده"),
        ("cancelled", "لغو شده"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "پرداخت نشده"),
        ("paid", "پرداخت شده"),
        ("failed", "ناموفق"),
    ]

    SHIPPING_METHOD_CHOICES = [
        ("courier", "پیک موتوری"),
        ("tipax", "تیپاکس"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="کاربر"
    )

    order_number = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="شماره سفارش"
    )

    # Snapshot اطلاعات گیرنده
    recipient_name = models.CharField(
        max_length=100,
        verbose_name="نام گیرنده"
    )

    phone = models.CharField(
        max_length=11,
        verbose_name="شماره تلفن"
    )

    state = models.CharField(
        max_length=100,
        verbose_name="استان"
    )

    city = models.CharField(
        max_length=100,
        verbose_name="شهر"
    )

    postal_code = models.CharField(
        max_length=10,
        verbose_name="کد پستی"
    )

    complete_address = models.TextField(
        verbose_name="آدرس کامل"
    )

    shipping_method = models.CharField(
        max_length=20,
        choices=SHIPPING_METHOD_CHOICES,
        verbose_name="روش ارسال"
    )

    # چون ارسال پس‌کرایه است
    shipping_price = models.PositiveIntegerField(
        default=0,
        verbose_name="هزینه ارسال"
    )

    original_price = models.PositiveIntegerField(
        verbose_name="مبلغ اصلی سفارش"
    )

    total_price = models.PositiveIntegerField(
        verbose_name="مبلغ نهایی سفارش"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="وضعیت سفارش"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="unpaid",
        verbose_name="وضعیت پرداخت"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    def __str__(self):
        return self.order_number

    class Meta:
        ordering = ["-created_at"]

        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status="pending"),
                name="unique_pending_order_per_user",
            )
        ]


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش"
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="محصول"
    )

    # Snapshot محصول در زمان خرید
    product_name = models.CharField(
        max_length=200,
        verbose_name="نام محصول"
    )

    color = models.CharField(max_length=50)

    price = models.PositiveIntegerField(
        verbose_name="قیمت واحد"
    )

    quantity = models.PositiveIntegerField(
        verbose_name="تعداد"
    )

    total_price = models.PositiveIntegerField(
        verbose_name="مبلغ کل"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product_name} - {self.quantity}"

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"