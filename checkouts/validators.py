from rest_framework import serializers


SHIPPING_METHODS = {
    "courier": "پیک موتوری",
    "tipax": "تیپاکس",
}


def validate_shipping_method(value):
    if value not in SHIPPING_METHODS:
        raise serializers.ValidationError(
            "روش ارسال نامعتبر است."
        )

    return value 