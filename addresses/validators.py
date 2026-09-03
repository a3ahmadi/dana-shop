import re

from rest_framework import serializers


def validate_phone(value):
    if not re.fullmatch(r"09\d{9}", value):
        raise serializers.ValidationError(
            "شماره تلفن باید 11 رقم و با 09 شروع شود."
        )

    return value


def validate_postal_code(value):
    if not re.fullmatch(r"\d{10}", value):
        raise serializers.ValidationError(
            "کد پستی باید دقیقا 10 رقم باشد."
        )

    return value