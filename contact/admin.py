from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Contact

# Register your models here.


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "phone_number",
        "email",
        "subject",
        "message",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "phone_number", "email", "subject", "message")
