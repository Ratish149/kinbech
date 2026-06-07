import django_filters

from .models import Category, Product, ProductReview, Subcategory


class CategoryFilter(django_filters.FilterSet):
    is_featured = django_filters.BooleanFilter(field_name="is_featured")

    class Meta:
        model = Category
        fields = ["is_featured"]


class SubcategoryFilter(django_filters.FilterSet):
    is_featured = django_filters.BooleanFilter(field_name="is_featured")

    class Meta:
        model = Subcategory
        fields = ["is_featured"]


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category__slug", lookup_expr="exact"
    )
    subcategory = django_filters.CharFilter(
        field_name="subcategory__slug", lookup_expr="exact"
    )
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    is_featured = django_filters.BooleanFilter(field_name="is_featured")
    is_best_seller = django_filters.BooleanFilter(field_name="is_best_seller")

    class Meta:
        model = Product
        fields = [
            "category",
            "subcategory",
            "min_price",
            "max_price",
            "is_featured",
            "is_best_seller",
        ]


class ProductReviewFilter(django_filters.FilterSet):
    product = django_filters.CharFilter(field_name="product__slug", lookup_expr="exact")
    user = django_filters.CharFilter(field_name="user__username", lookup_expr="exact")

    class Meta:
        model = ProductReview
        fields = ["product", "user"]
