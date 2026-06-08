from django.db.models import Prefetch
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from kinbech.utils.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly

from .filters import (
    CategoryFilter,
    ProductFilter,
    ProductReviewFilter,
    SubcategoryFilter,
)
from .models import Category, Product, ProductImage, ProductReview, Subcategory
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductReviewSerializer,
    ProductSerializer,
    SubcategorySerializer,
)


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.prefetch_related(
        Prefetch(
            "subcategories",
            queryset=Subcategory.objects.only(
                "id", "slug", "name", "category_id", "is_featured"
            ),
        )
    ).only("id", "slug", "name", "is_featured")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.prefetch_related(
        Prefetch(
            "subcategories",
            queryset=Subcategory.objects.only(
                "id", "slug", "name", "category_id", "is_featured"
            ),
        )
    ).only("id", "slug", "name", "is_featured")
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = [IsAdminOrReadOnly]


class SubcategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = SubcategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SubcategoryFilter

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        queryset = Subcategory.objects.select_related("category").only(
            "id", "slug", "name", "is_featured", "category__id", "category__slug"
        )
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def perform_create(self, serializer):
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                serializer.save(category=category)
            except Category.DoesNotExist:
                raise Http404("Category not found.")
        else:
            serializer.save()


class SubcategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubcategorySerializer
    lookup_field = "slug"
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        queryset = Subcategory.objects.select_related("category").only(
            "id", "slug", "name", "is_featured", "category__id", "category__slug"
        )
        if category_slug:
            return queryset.filter(category__slug=category_slug)
        return queryset


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ["name"]
    ordering_fields = ["price", "created_at", "average_rating_annotated"]
    ordering = ["-created_at"]

    def get_queryset(self):
        from django.db.models import Avg, Count

        qs = Product.objects.select_related("category", "subcategory").annotate(
            average_rating_annotated=Avg("reviews__rating"),
            total_reviews_annotated=Count("reviews", distinct=True),
        )
        if self.request.method == "GET":
            return qs.only(
                "id",
                "slug",
                "name",
                "price",
                "market_price",
                "thumbnail_image",
                "thumbnail_alt",
                "unit",
                "stock",
                "is_featured",
                "is_best_seller",
                "meta_title",
                "meta_description",
                "category__id",
                "category__slug",
                "category__name",
                "subcategory__id",
                "subcategory__slug",
                "subcategory__name",
            )
        return qs

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProductListSerializer
        return ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    lookup_field = "slug"
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        from django.db.models import Avg, Count

        return (
            Product.objects
            .select_related("category", "subcategory")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.only("id", "image", "product_id"),
                )
            )
            .annotate(
                average_rating_annotated=Avg("reviews__rating"),
                total_reviews_annotated=Count("reviews", distinct=True),
            )
            .only(
                "id",
                "slug",
                "name",
                "price",
                "market_price",
                "thumbnail_image",
                "thumbnail_alt",
                "unit",
                "description",
                "stock",
                "is_featured",
                "is_best_seller",
                "meta_title",
                "meta_description",
                "category__id",
                "category__slug",
                "subcategory__id",
                "subcategory__slug",
            )
        )

    def get_object(self):
        """
        Support retrieving by both numeric ID or unique slug.
        """
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs.get(lookup_url_kwarg) or self.kwargs.get("slug")

        if not lookup_value:
            raise Http404("No slug or ID was provided.")

        # Try to retrieve by ID first if it is numeric
        if lookup_value.isdigit():
            try:
                return queryset.get(pk=lookup_value)
            except Product.DoesNotExist:
                pass

        # Fallback to slug lookup
        try:
            return queryset.get(slug=lookup_value)
        except Product.DoesNotExist:
            raise Http404("No product matches the given query.")


class ProductReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductReviewFilter

    def get_queryset(self):
        return ProductReview.objects.select_related("user", "product").only(
            "id",
            "user_id",
            "product_id",
            "rating",
            "comment",
            "created_at",
            "user__id",
            "user__username",
            "product__id",
            "product__slug",
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return ProductReview.objects.select_related("user", "product").only(
            "id",
            "user_id",
            "product_id",
            "rating",
            "comment",
            "created_at",
            "user__id",
            "user__username",
            "product__id",
            "product__slug",
        )
