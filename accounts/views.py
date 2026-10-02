from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import time

from .models import User
from .serializers import RequestOTPSerializer, VerifyOTPSerializer, ProfileSerializer
from .services import generate_otp, hash_otp, verify_otp, get_otp_expiration
from .sms import OTPDeliveryError, send_otp_sms
from .redirects import safe_next_url


def _client_ip(request):
    # REMOTE_ADDR is supplied by the web server. Never trust a client-supplied X-Forwarded-For.
    return request.META.get("REMOTE_ADDR", "unknown")


@method_decorator([csrf_protect, never_cache], name="dispatch")
class RequestOTPView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        ip_key = f"otp:requests:ip:{_client_ip(request)}"
        cache.add(ip_key, 0, timeout=3600)
        if cache.incr(ip_key) > settings.OTP_REQUESTS_PER_IP_HOUR:
            return Response({"message": "Too many requests. Try again later."}, status=429)

        lock_key = f"otp:lock:{phone_number}"
        if not cache.add(lock_key, True, timeout=20):
            return Response({"message": "Please wait before requesting another code."}, status=429)
        try:
            cooldown_key = f"otp:cooldown:{phone_number}"
            if cache.get(cooldown_key):
                return Response({"message": "Please wait before requesting another code."}, status=429)
            otp = generate_otp()
            otp_key = f"otp:{phone_number}"
            cache.set(otp_key, {
                "code": hash_otp(otp),
                "attempts": 0,
                "expires_at": get_otp_expiration(),
            }, timeout=settings.OTP_EXPIRATION_SECONDS)
            try:
                send_otp_sms(phone_number, otp)
            except OTPDeliveryError:
                cache.delete(otp_key)
                return Response({"message": "Sending the code failed. Please try again later."}, status=503)
            cache.set(cooldown_key, True, timeout=settings.OTP_RESEND_COOLDOWN_SECONDS)
            return Response({"message": "Verification code sent.", "retry_after": settings.OTP_RESEND_COOLDOWN_SECONDS})
        finally:
            cache.delete(lock_key)


@method_decorator([csrf_protect, never_cache], name="dispatch")
class VerifyOTPView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]
        ip_key = f"otp:verifications:ip:{_client_ip(request)}"
        cache.add(ip_key, 0, timeout=3600)
        if cache.incr(ip_key) > settings.OTP_VERIFICATIONS_PER_IP_HOUR:
            return Response({"message": "Too many requests. Try again later."}, status=429)
        lock_key = f"otp:lock:{phone_number}"
        if not cache.add(lock_key, True, timeout=20):
            return Response({"message": "Please try again shortly."}, status=429)
        try:
            otp_key = f"otp:{phone_number}"
            otp_data = cache.get(otp_key)
            if not otp_data or time.time() >= otp_data["expires_at"]:
                cache.delete(otp_key)
                return Response({"message": "Code expired or does not exist."}, status=400)
            if otp_data["attempts"] >= settings.OTP_MAX_ATTEMPTS:
                cache.delete(otp_key)
                return Response({"message": "Too many incorrect codes."}, status=429)
            if not verify_otp(otp, otp_data["code"]):
                otp_data["attempts"] += 1
                if otp_data["attempts"] >= settings.OTP_MAX_ATTEMPTS:
                    cache.delete(otp_key)
                    return Response({"message": "Too many incorrect codes."}, status=429)
                remaining = max(1, int(otp_data["expires_at"] - time.time()))
                cache.set(otp_key, otp_data, timeout=remaining)
                return Response({"message": "Incorrect code."}, status=400)

            # Consume before creating a session. The per-phone cache lock prevents replay.
            cache.delete(otp_key)
            user, _ = User.objects.get_or_create(phone_number=phone_number, defaults={"password": make_password(None)})
            if not user.is_active or user.is_staff or user.is_superuser:
                return Response({"message": "Account is inactive."}, status=403)
            login(request._request, user, backend="django.contrib.auth.backends.ModelBackend")
            return Response({"message": "Signed in.", "redirect_url": safe_next_url(request._request, request.data.get("next"))})
        finally:
            cache.delete(lock_key)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user.profile).data)

    def patch(self, request):
        serializer = ProfileSerializer(request.user.profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
