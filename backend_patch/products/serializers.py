from rest_framework import serializers

from .models import (
    Category,
    Color,
    Product,
    ProductImage,
)


class CategorySerializer(serializers.ModelSerializer):

    product_count = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "slug",
            "image",
            "product_count",
        ]


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = [
            "id",
            "name",
            "hex_code",
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage

        fields = [
            "id",
            "image",
        ]


class ProductListSerializer(serializers.ModelSerializer):

    final_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=0,
        read_only=True
    )

    category = serializers.CharField(
        source="category.name",
        read_only=True
    )

    colors = ColorSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "price",
            "discount_percent",
            "final_price",
            "stock",
            "main_image",
            "colors",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):

    final_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=0,
        read_only=True
    )

    category = CategorySerializer(
        read_only=True
    )
    images = ProductImageSerializer(
        many=True,
        read_only=True
    )
    colors = ColorSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "price",
            "discount_percent",
            "final_price",
            "stock",
            "sku",
            "main_image",
            "images",
            "colors",
            "created_at",
        ]
