import re
from rest_framework import serializers
from .models import Profile

_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_phone(value):
    value = value.translate(_DIGITS).strip().replace(" ", "").replace("-", "")
    if value.startswith("+98"):
        value = "0" + value[3:]
    elif value.startswith("0098"):
        value = "0" + value[4:]
    elif value.startswith("9") and len(value) == 10:
        value = "0" + value
    if not re.fullmatch(r"09[0-9]{9}", value):
        raise serializers.ValidationError("شماره موبایل معتبر نیست.")
    return value


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=32)

    def validate_phone_number(self, value):
        return normalize_phone(value)


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=32)
    otp = serializers.CharField(min_length=6, max_length=6, trim_whitespace=True)

    def validate_phone_number(self, value):
        return normalize_phone(value)

    def validate_otp(self, value):
        value = value.translate(_DIGITS)
        if not re.fullmatch(r"[0-9]{6}", value):
            raise serializers.ValidationError("کد تأیید باید شش رقم باشد.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "first_name", "last_name", "birth", "gender", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
