from rest_framework import serializers

from addresses.models import Address

from .validators import available_shipping_methods, validate_shipping_method


class CheckoutSerializer(serializers.Serializer):

    address_id = serializers.IntegerField(
        min_value=1
    )

    shipping_method = serializers.CharField(
        validators=[validate_shipping_method]
    )
    payment_method = serializers.ChoiceField(choices=["online"], default="online")

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
        profile = request.user.profile
        if not profile.first_name.strip() or not profile.last_name.strip():
            raise serializers.ValidationError({"profile": "نام و نام خانوادگی را کامل کنید."})
        address = Address.objects.get(id=attrs["address_id"], user=request.user)
        if attrs["shipping_method"] not in available_shipping_methods(address.city):
            raise serializers.ValidationError({"shipping_method": "روش ارسال با شهر آدرس انتخابی سازگار نیست."})
        return attrs
