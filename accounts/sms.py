import requests
from django.conf import settings


class OTPDeliveryError(Exception):
    pass


def send_otp_sms(phone_number, otp):
    username = settings.MELIPAYAMAK_USERNAME
    password = settings.MELIPAYAMAK_PASSWORD
    body_id = settings.MELIPAYAMAK_BODY_ID
    if not (username and password and body_id):
        raise OTPDeliveryError("Melipayamak credentials or body ID are missing")
    try:
        response = requests.post(
            "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber",
            data={"username": username, "password": password, "text": otp, "to": phone_number, "bodyId": body_id},
            timeout=8,
        )
        response.raise_for_status()
        result = response.json()
        if not isinstance(result, dict) or result.get("RetStatus") != 1:
            raise OTPDeliveryError("Melipayamak rejected OTP delivery")
    except (requests.RequestException, ValueError) as exc:
        raise OTPDeliveryError("Melipayamak delivery failed") from exc
