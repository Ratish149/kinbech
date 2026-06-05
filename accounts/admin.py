from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(ModelAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email", "phone_number", "first_name", "last_name")
