from rest_framework import serializers

from .models import Address
from .validators import validate_phone, validate_postal_code


class AddressSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(
        validators=[validate_phone]
    )

    postal_code = serializers.CharField(
        validators=[validate_postal_code]
    )

    class Meta:
        model = Address
        fields = [
            "id",
            "title",
            "recipient_name",
            "phone",
            "state",
            "city",
            "postal_code",
            "complete_address",
            "is_default",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "عنوان آدرس نمی‌تواند خالی باشد."
            )

        if len(value) > 100:
            raise serializers.ValidationError(
                "عنوان آدرس نمی‌تواند بیشتر از 100 کاراکتر باشد."
            )

        return value

    def validate_recipient_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "نام گیرنده نمی‌تواند خالی باشد."
            )

        return value

    def validate_state(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "استان نمی‌تواند خالی باشد."
            )

        return value

    def validate_city(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "شهر نمی‌تواند خالی باشد."
            )

        return value

    def validate_complete_address(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "آدرس کامل نمی‌تواند خالی باشد."
            )

        return value

    def validate(self, attrs):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return attrs

        # فقط هنگام ایجاد آدرس بررسی شود
        if self.instance is None:

            address_count = Address.objects.filter(
                user=request.user
            ).count()

            if address_count >= 3:
                raise serializers.ValidationError({
                    "detail": "حداکثر ۳ آدرس برای هر کاربر مجاز است."
                })

        return attrs