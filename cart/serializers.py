from rest_framework import serializers


class AddToCartSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()

    quantity = serializers.IntegerField(
        min_value=1
    )


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

    color = serializers.CharField(
        source="product.color.name",
        allow_null=True
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