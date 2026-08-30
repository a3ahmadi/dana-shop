import re

from rest_framework import serializers
from .models import Profile


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)

    def validate_phone_number(self, value):
        pattern = r"^09\d{9}$"

        if not re.fullmatch(pattern, value):
            raise serializers.ValidationError(
                "شماره تماس باید به شکل 09123456789 باشد."
            )

        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)

    otp = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    def validate_phone_number(self, value):
        pattern = r"^09\d{9}$"

        if not re.fullmatch(pattern, value):
            raise serializers.ValidationError(
                "شماره تماس باید به شکل 09123456789 باشد."
            )

        return value

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "کد تایید باید فقط شامل عدد باشد."
            )

        return value


class ProfileSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(
        source="user.phone",
        read_only=True
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "phone",
            "first_name",
            "last_name",
            "email",
            "birth",
            "gender",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
