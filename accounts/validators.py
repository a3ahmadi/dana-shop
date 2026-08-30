import re

from django.core.exceptions import ValidationError


def validate_phone_number(value):
    pattern = r"^09\d{9}$"

    if not re.fullmatch(pattern, value):
        raise ValidationError(
            "Phone number must be in this format: 09123456789"
        )