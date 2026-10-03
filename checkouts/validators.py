from rest_framework import serializers


SHIPPING_METHODS = {
    "courier": "پیک موتوری",
    "tipax": "تیپاکس",
}


def available_shipping_methods(city):
    normalized = " ".join(city.strip().replace("ي", "ی").split())
    return ("courier", "tipax") if normalized == "تهران" else ("tipax",)


def shipping_for_city(city):
    return available_shipping_methods(city)[0]


def validate_shipping_method(value):
    if value not in SHIPPING_METHODS:
        raise serializers.ValidationError(
            "روش ارسال نامعتبر است."
        )

    return value
