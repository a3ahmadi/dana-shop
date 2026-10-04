from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0005_order_unique_pending_order_per_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="tracking_code",
            field=models.CharField(blank=True, default="", max_length=100, verbose_name="کد رهگیری ارسال"),
        ),
    ]
