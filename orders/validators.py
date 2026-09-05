from rest_framework import serializers


def validate_shipping_method(value):

    allowed_methods = {
        "courier",
        "tipax",
    }

    if value not in allowed_methods:
        raise serializers.ValidationError(
            "روش ارسال نامعتبر است."
        )

    return value