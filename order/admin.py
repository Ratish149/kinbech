from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Order, OrderItem


class OrderItemInline(TabularInline):
    model = OrderItem
    tab = True
    extra = 0


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        "order_id",
        "full_name",
        "phone_number",
        "total_amount",
        "status",
        "payment_method",
        "is_paid",
        "created_at",
    ]
    list_filter = ["status", "payment_method", "is_paid", "created_at"]
    search_fields = ["order_id", "full_name", "phone_number", "transaction_id"]
    readonly_fields = ["order_id", "created_at", "updated_at"]
    inlines = [OrderItemInline]
