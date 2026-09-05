from rest_framework import serializers
from products.models import Product, Color


class AddToCartSerializer(serializers.Serializer):

    product_id = serializers.IntegerField(min_value=1)

    color_id = serializers.IntegerField(min_value=1)

    quantity = serializers.IntegerField(
        min_value=1
    )

    def validate(self, attrs):

        product_id = attrs["product_id"]
        color_id = attrs["color_id"]

        product = Product.objects.filter(
            id=product_id,
            is_active=True
        ).first()

        if not product:
            raise serializers.ValidationError({
                "product_id": "محصول پیدا نشد."
            })

        color = Color.objects.filter(
            id=color_id,
            is_active=True
        ).first()

        if not color:
            raise serializers.ValidationError({
                "color_id": "رنگ پیدا نشد."
            })

        if not product.colors.filter(id=color_id).exists():
            raise serializers.ValidationError({
                "color_id": "این رنگ برای محصول مورد نظر موجود نیست."
            })

        attrs["product"] = product
        attrs["color"] = color

        return attrs


class UpdateCartItemSerializer(serializers.Serializer):

    quantity = serializers.IntegerField(
        min_value=1
    )


class CartItemSerializer(serializers.Serializer):

    product_id = serializers.IntegerField(
        source="product.id"
    )

    name = serializers.CharField(
        source="product.name"
    )

    slug = serializers.CharField(
        source="product.slug"
    )

    main_image = serializers.ImageField(
        source="product.main_image"
    )

    color_id = serializers.IntegerField(
        source="color.id"
    )

    color = serializers.CharField(
        source="color.name"
    )

    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    final_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    quantity = serializers.IntegerField()

    total = serializers.DecimalField(
        max_digits=12,
        decimal_places=0
    )