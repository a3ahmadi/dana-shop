from django.core.cache import cache
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
import time
from rest_framework.permissions import IsAuthenticated
from .serializers import RequestOTPSerializer, VerifyOTPSerializer, ProfileSerializer
from .services import (
    generate_otp,
    hash_otp,
    verify_otp,
    get_otp_expiration,
    generate_tokens_for_user,
)
from .models import User


class RequestOTPView(APIView):

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        cooldown_key = f"otp:cooldown:{phone_number}"

        if cache.get(cooldown_key):
            return Response(
                {
                    "message": "Please wait before requesting a new OTP."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        otp = generate_otp()

        otp_key = f"otp:{phone_number}"

        otp_data = {
            "code": hash_otp(otp),
            "attempts": 0,
            "expires_at": get_otp_expiration(),
        }

        cache.set(
            otp_key,
            otp_data,
            timeout=settings.OTP_EXPIRATION_SECONDS,
        )

        cache.set(
            cooldown_key,
            True,
            timeout=settings.OTP_RESEND_COOLDOWN_SECONDS,
        )

        print(
            f"\n"
            f"Phone Number: {phone_number}\n"
            f"OTP Code: {otp}\n"
        )

        return Response(
            {
                "message": "OTP code generated successfully.",
                "Phone Number": phone_number,
                "otp": otp,
            },
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]

        otp_key = f"otp:{phone_number}"

        otp_data = cache.get(otp_key)

        if not otp_data:
            return Response(
                {
                    "message": "OTP expired or does not exist."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if time.time() >= otp_data["expires_at"]:
            cache.delete(otp_key)

            return Response(
                {
                    "message": "OTP expired."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp_data["attempts"] >= settings.OTP_MAX_ATTEMPTS:
            cache.delete(otp_key)

            return Response(
                {
                    "message": "Maximum OTP attempts exceeded."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if not verify_otp(
            otp,
            otp_data["code"],
        ):
            otp_data["attempts"] += 1

            if otp_data["attempts"] >= settings.OTP_MAX_ATTEMPTS:
                cache.delete(otp_key)

                return Response(
                    {
                        "message": "Maximum OTP attempts exceeded."
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            remaining_seconds = max(
                1,
                int(
                    otp_data["expires_at"]
                    - time.time()
                ),
            )

            cache.set(
                otp_key,
                otp_data,
                timeout=remaining_seconds,
            )

            return Response(
                {
                    "message": "Invalid OTP."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # OTP is valid
        cache.delete(otp_key)

        user, created = User.objects.get_or_create(
            phone_number=phone_number
        )

        if not user.is_active:
            return Response(
                {
                    "message": "User account is inactive."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        tokens = generate_tokens_for_user(user)

        return Response(
            {
                "message": "OTP verified successfully.",
                "user": {
                    "id": user.id,
                    "phone_number": user.phone_number,
                },
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )

class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = ProfileSerializer(
            request.user.profile
        )

        return Response(serializer.data)

    def patch(self, request):

        serializer = ProfileSerializer(
            request.user.profile,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)