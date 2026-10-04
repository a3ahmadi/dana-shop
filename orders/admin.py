from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "product_name", "color", "price", "quantity", "total_price")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "payment_status", "total_price", "created_at")
    search_fields = ("order_number",)
    list_filter = ("status", "payment_status")
    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "color", "quantity", "price", "total_price")
    search_fields = ("order__order_number", "product_name")
    list_select_related = ("order", "product")
    readonly_fields = ("order", "product", "product_name", "color", "price", "quantity", "total_price")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
