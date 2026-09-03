from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Address
from .serializers import AddressSerializer


class AddressListCreateAPIView(generics.ListCreateAPIView):

    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class AddressDetailAPIView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(
            user=self.request.user
        )


class AddressSetDefaultAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        address = Address.objects.filter(
            id=pk,
            user=request.user
        ).first()

        if not address:
            return Response(
                {
                    "detail": "آدرس مورد نظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        address.is_default = True
        address.save()

        return Response(
            {
                "detail": "آدرس پیش‌فرض با موفقیت تغییر کرد.",
                "address": AddressSerializer(
                    address,
                    context={"request": request}
                ).data
            },
            status=status.HTTP_200_OK
        )