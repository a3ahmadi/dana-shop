from rest_framework import serializers

from addresses.models import Address

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