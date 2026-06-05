from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Testimonial


# Register your models here.
@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ("name", "rating", "created_at", "updated_at")
    list_filter = ("rating", "created_at", "updated_at")
    search_fields = ("name", "rating", "created_at", "updated_at")
