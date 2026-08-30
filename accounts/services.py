import hashlib
import hmac
import secrets
import time

from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(),
        otp.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_otp(otp: str, hashed_otp: str) -> bool:
    expected_hash = hash_otp(otp)

    return hmac.compare_digest(
        expected_hash,
        hashed_otp,
    )


def get_otp_expiration():
    return int(time.time()) + settings.OTP_EXPIRATION_SECONDS


def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }