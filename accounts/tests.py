import json
from unittest.mock import Mock, patch

from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import User
from .services import hash_otp
from .sms import OTPDeliveryError, send_otp_sms


TEST_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "otp-tests"}}
PHONE = "09123456789"
CODE = "123456"


@override_settings(CACHES=TEST_CACHE, OTP_REQUESTS_PER_IP_HOUR=10)
class OTPLoginTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client(enforce_csrf_checks=True)
        page = self.client.get(reverse("storefront:login"))
        self.assertEqual(page.status_code, 200)
        self.csrf = self.client.cookies[settings.CSRF_COOKIE_NAME].value

    def post(self, name, payload, client=None):
        return (client or self.client).post(
            reverse(name), data=json.dumps(payload), content_type="application/json",
            HTTP_X_CSRFTOKEN=self.csrf,
        )

    def request_code(self, sender, phone=PHONE):
        response = self.post("accounts:request-otp", {"phone_number": phone})
        self.assertEqual(response.status_code, 200)
        sender.assert_called_once()
        return response

    @patch("accounts.views.generate_otp", return_value=CODE)
    @patch("accounts.views.send_otp_sms")
    def test_request_does_not_expose_code_and_normalizes_phone(self, sender, generator):
        response = self.post("accounts:request-otp", {"phone_number": "\u06f0\u06f9\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9"})
        self.assertEqual(response.status_code, 200, response.content)
        self.assertNotIn(CODE, response.content.decode())
        self.assertNotIn("otp", response.json())
        sender.assert_called_once_with(PHONE, CODE)
        self.assertEqual(cache.get(f"otp:{PHONE}")["code"], hash_otp(CODE))
        self.assertEqual(self.post("accounts:request-otp", {"phone_number": PHONE}).status_code, 429)

    @patch("accounts.views.generate_otp", return_value=CODE)
    @patch("accounts.views.send_otp_sms")
    def test_verify_creates_session_without_password_or_profile_input(self, sender, generator):
        self.request_code(sender)
        response = self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": CODE, "next": "/products/?search=pen"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["redirect_url"], "/products/?search=pen")
        self.assertNotIn("tokens", response.json())
        user = User.objects.get(phone_number=PHONE)
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.profile.first_name, "")
        self.assertEqual(self.client.get(reverse("accounts:profile")).status_code, 200)
        self.assertEqual(self.client.patch(reverse("accounts:profile"), data="{}", content_type="application/json").status_code, 403)
        self.assertEqual(self.client.get(reverse("storefront:login")).status_code, 302)
        self.csrf = self.client.cookies[settings.CSRF_COOKIE_NAME].value
        self.assertEqual(self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": CODE}).status_code, 400)

    @patch("accounts.views.generate_otp", return_value=CODE)
    @patch("accounts.views.send_otp_sms")
    def test_rejects_external_next(self, sender, generator):
        self.request_code(sender)
        response = self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": CODE, "next": "//evil.example/"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["redirect_url"], "/")
        page = self.client.get(reverse("storefront:login") + "?next=https://evil.example/")
        self.assertEqual(page["Location"], "/")

    @patch("accounts.views.generate_otp", return_value=CODE)
    @patch("accounts.views.send_otp_sms")
    def test_attempt_limit_and_expiry(self, sender, generator):
        self.request_code(sender)
        for _ in range(settings.OTP_MAX_ATTEMPTS - 1):
            self.assertEqual(self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": "000000"}).status_code, 400)
        self.assertEqual(self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": "000000"}).status_code, 429)
        self.assertEqual(self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": CODE}).status_code, 400)
        self.assertFalse(User.objects.filter(phone_number=PHONE).exists())
        cache.set(f"otp:{PHONE}", {"code": hash_otp(CODE), "attempts": 0, "expires_at": 0}, timeout=120)
        self.assertEqual(self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": CODE}).status_code, 400)

    @patch("accounts.views.send_otp_sms", side_effect=OTPDeliveryError("delivery failed"))
    def test_failed_delivery_does_not_leave_active_code(self, sender):
        response = self.post("accounts:request-otp", {"phone_number": PHONE})
        self.assertEqual(response.status_code, 503)
        self.assertIsNone(cache.get(f"otp:{PHONE}"))
        self.assertIsNone(cache.get(f"otp:cooldown:{PHONE}"))

    @patch("accounts.views.send_otp_sms")
    def test_ip_request_limit(self, sender):
        with override_settings(OTP_REQUESTS_PER_IP_HOUR=1):
            self.request_code(sender)
            response = self.post("accounts:request-otp", {"phone_number": "09111111111"})
            self.assertEqual(response.status_code, 429)
            self.assertEqual(sender.call_count, 1)

    def test_csrf_required_for_both_endpoints(self):
        anonymous = Client(enforce_csrf_checks=True)
        for name in ("accounts:request-otp", "accounts:verify-otp"):
            response = anonymous.post(reverse(name), data=json.dumps({"phone_number": PHONE, "otp": CODE}), content_type="application/json")
            self.assertEqual(response.status_code, 403)

    def test_invalid_input_and_missing_code_do_not_login(self):
        self.assertEqual(self.post("accounts:request-otp", {"phone_number": "091\u0662\u0663\u0664\u0665\u0666\u06678x"}).status_code, 400)
        self.assertEqual(self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": "abcdef"}).status_code, 400)
        self.assertEqual(self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": CODE}).status_code, 400)
        self.assertFalse(User.objects.exists())

    @patch("accounts.views.generate_otp", return_value=CODE)
    @patch("accounts.views.send_otp_sms")
    def test_inactive_and_staff_users_cannot_use_customer_otp(self, sender, generator):
        user = User.objects.create_user(PHONE, is_active=False)
        self.request_code(sender)
        self.assertEqual(self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": CODE}).status_code, 403)
        self.assertNotIn("_auth_user_id", self.client.session)
        user.is_active = True
        user.is_staff = True
        user.save()
        cache.set(f"otp:{PHONE}", {"code": hash_otp(CODE), "attempts": 0, "expires_at": 9999999999}, timeout=120)
        self.assertEqual(self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": CODE}).status_code, 403)


    def test_login_page_has_only_phone_and_code_forms(self):
        content = self.client.get(reverse("storefront:login")).content.decode()
        self.assertIn('id="authForm"', content)
        self.assertIn('id="otpForm"', content)
        self.assertIn('storefront/js/login.js', content)
        self.assertNotIn('type="password"', content)
        self.assertNotIn('name="first_name"', content)

    @override_settings(OTP_VERIFICATIONS_PER_IP_HOUR=1)
    def test_verify_ip_rate_limit(self):
        self.assertEqual(self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": CODE}).status_code, 400)
        self.assertEqual(self.post("accounts:verify-otp", {"phone_number": PHONE, "otp": CODE}).status_code, 429)

class MelipayamakTests(TestCase):
    @override_settings(MELIPAYAMAK_USERNAME="", MELIPAYAMAK_PASSWORD="", MELIPAYAMAK_BODY_ID="")
    def test_missing_configuration_fails_closed(self):
        with self.assertRaises(OTPDeliveryError):
            send_otp_sms(PHONE, CODE)

    @override_settings(MELIPAYAMAK_USERNAME="user", MELIPAYAMAK_PASSWORD="secret", MELIPAYAMAK_BODY_ID="123")
    @patch("accounts.sms.requests.post")
    def test_provider_payload_and_status(self, post):
        response = Mock()
        response.json.return_value = {"RetStatus": 1, "Value": "receipt"}
        post.return_value = response
        send_otp_sms(PHONE, CODE)
        kwargs = post.call_args.kwargs
        self.assertEqual(kwargs["data"], {"username": "user", "password": "secret", "text": CODE, "to": PHONE, "bodyId": "123"})
        self.assertEqual(kwargs["timeout"], 8)
        response.json.return_value = {"RetStatus": 0}
        with self.assertRaises(OTPDeliveryError):
            send_otp_sms(PHONE, CODE)
