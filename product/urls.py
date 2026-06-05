from django.urls import path

from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    ProductDetailView,
    ProductListCreateView,
    ProductReviewDetailView,
    ProductReviewListCreateView,
    SubcategoryDetailView,
    SubcategoryListCreateView,
)

urlpatterns = [
    # Categories
    path("categories/", CategoryListCreateView.as_view(), name="category-list"),
    path(
        "categories/<str:slug>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
    path(
        "categories/<str:category_slug>/subcategories/",
        SubcategoryListCreateView.as_view(),
        name="subcategory-list",
    ),
    path(
        "categories/<str:category_slug>/subcategories/<str:slug>/",
        SubcategoryDetailView.as_view(),
        name="subcategory-detail",
    ),
    # Products flat
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<str:slug>/", ProductDetailView.as_view(), name="product-detail"),
    # Reviews
    path(
        "reviews/",
        ProductReviewListCreateView.as_view(),
        name="review-list-create",
    ),
    path(
        "reviews/<int:pk>/",
        ProductReviewDetailView.as_view(),
        name="review-detail",
    ),
]
