from django.db import models


class Payment(models.Model):

    STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("success", "موفق"),
        ("failed", "ناموفق"),
    ]

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payment",
        verbose_name="سفارش"
    )

    amount = models.PositiveIntegerField(
        verbose_name="مبلغ پرداخت"
    )

    authority = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="شناسه پرداخت"
    )

    ref_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="شماره پیگیری"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="وضعیت پرداخت"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"