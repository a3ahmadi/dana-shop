from rest_framework import serializers

from addresses.models import Address
from cart.cart import Cart
from checkouts.state import cart_signature
from checkouts.validators import available_shipping_methods
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

    def validate(self, attrs):
        request = self.context["request"]
        selected = request.session.get("checkout") or {}
        if (
            selected.get("address_id") != attrs["address_id"]
            or selected.get("shipping_method") != attrs["shipping_method"]
            or selected.get("payment_method") != "online"
            or selected.get("cart_signature") != cart_signature(list(Cart(request)))
        ):
            raise serializers.ValidationError("اطلاعات سفارش تغییر کرده است. جزئیات سفارش را دوباره تأیید کنید.")
        address = Address.objects.get(id=attrs["address_id"], user=request.user)
        if attrs["shipping_method"] not in available_shipping_methods(address.city):
            raise serializers.ValidationError("روش ارسال با شهر انتخابی سازگار نیست.")
        profile = request.user.profile
        if not profile.first_name.strip() or not profile.last_name.strip():
            raise serializers.ValidationError("نام و نام خانوادگی را کامل کنید.")
        return attrs


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
            "tracking_code",
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
            "tracking_code",
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

        if order.status not in ("pending", "processing"):
            raise serializers.ValidationError(
                "این سفارش قابل لغو نیست."
            )

        if order.status == "pending" and order.payment_status == "paid":
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
