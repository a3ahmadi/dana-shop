from rest_framework import serializers

from addresses.models import Address
from .models import OrderItem, Order

from .validators import validate_shipping_method


class CreateOrderSerializer(serializers.Serializer):

    address_id = serializers.IntegerField(
        min_value=1
    )

    shipping_method = serializers.CharField(
        validators=[validate_shipping_method]
    )

    def validate_address_id(self, value):

        request = self.context["request"]

        exists = Address.objects.filter(
            id=value,
            user=request.user
        ).exists()

        if not exists:
            raise serializers.ValidationError(
                "آدرس مورد نظر پیدا نشد."
            )

        return value


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = [
            "product",
            "product_name",
            "color",
            "price",
            "quantity",
            "total_price",
        ]


class OrderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "total_price",
            "status",
            "payment_status",
            "shipping_method",
            "created_at",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",

            "recipient_name",
            "phone",
            "state",
            "city",
            "postal_code",
            "complete_address",

            "shipping_method",
            "shipping_price",

            "original_price",
            "total_price",

            "status",
            "payment_status",

            "created_at",
            "updated_at",

            "items",
        ]


class CancelOrderSerializer(serializers.Serializer):

    def validate(self, attrs):

        order = self.context["order"]

        if order.status != "pending":
            raise serializers.ValidationError(
                "این سفارش قابل لغو نیست."
            )

        if order.payment_status == "paid":
            raise serializers.ValidationError(
                "سفارش پرداخت شده قابل لغو نیست."
            )

        return attrs


class UpdateOrderStatusSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=[
            "processing",
            "shipping",
            "delivered",
            "cancelled",
        ]
    )

    def validate_status(self, value):

        order = self.context["order"]

        current_status = order.status

        allowed_transitions = {
            "pending": [
                "cancelled",
            ],
            "paid": [
                "processing",
            ],
            "processing": [
                "shipping",
            ],
            "shipping": [
                "delivered",
            ],
            "delivered": [],
            "cancelled": [],
        }

        allowed_statuses = allowed_transitions.get(
            current_status,
            []
        )

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"تغییر وضعیت از «{current_status}» "
                f"به «{value}» مجاز نیست."
            )

        return value