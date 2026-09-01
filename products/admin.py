from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductImage,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "is_active",
        "created_at",
    ]

    prepopulated_fields = {
        "slug": ("name",)
    }


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "name",
        "category",
        "price",
        "discount_percent",
        "stock",
        "is_active",
    ]

    list_filter = [
        "category",
        "is_active",
    ]

    search_fields = [
        "name",
        "sku",
    ]

    prepopulated_fields = {
        "slug": ("name",)
    }

    inlines = [
        ProductImageInline
    ]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "product",
        "created_at",
    ]