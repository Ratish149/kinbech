from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Category, Product, ProductImage, ProductReview, Subcategory


class ProductImageInline(TabularInline):
    model = ProductImage
    tab = True
    extra = 1


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subcategory)
class SubcategoryAdmin(ModelAdmin):
    list_display = ["name", "slug", "category"]
    list_filter = ["category"]
    search_fields = ["name", "slug", "category__name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = [
        "name",
        "category",
        "subcategory",
        "price",
        "market_price",
        "stock",
    ]
    list_filter = ["category", "subcategory"]
    search_fields = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = ["product", "image", "created_at"]
    list_filter = ["product"]


@admin.register(ProductReview)
class ProductReviewAdmin(ModelAdmin):
    list_display = ["product", "user", "rating", "created_at"]
    list_filter = ["rating", "created_at", "product"]
    search_fields = ["product__name", "user__username", "comment"]
