from rest_framework import serializers

from .models import Category, Product, ProductImage, ProductReview, Subcategory


class SubcategorySerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all(), required=False
    )

    class Meta:
        model = Subcategory
        fields = ["id", "slug", "name", "is_featured", "category"]


class SubcategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ["id", "slug", "name", "is_featured"]


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    subs = SubcategoryListSerializer(source="subcategories", many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "slug", "name", "is_featured", "image", "subs"]


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "name", "is_featured", "image"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )
    subcategory = serializers.SlugRelatedField(
        slug_field="slug", queryset=Subcategory.objects.all()
    )
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "name",
            "category",
            "subcategory",
            "price",
            "market_price",
            "image",
            "thumbnail_image",
            "thumbnail_alt",
            "unit",
            "description",
            "stock",
            "is_featured",
            "is_best_seller",
            "images",
            "uploaded_images",
            "average_rating",
            "total_reviews",
            "meta_title",
            "meta_description",
        ]

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        product = super().create(validated_data)
        for img in uploaded_images:
            ProductImage.objects.create(product=product, image=img)
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        product = super().update(instance, validated_data)
        for img in uploaded_images:
            ProductImage.objects.create(product=product, image=img)
        return product


class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer(read_only=True)
    subcategory = SubcategoryListSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "name",
            "category",
            "subcategory",
            "price",
            "market_price",
            "image",
            "thumbnail_image",
            "thumbnail_alt",
            "unit",
            "is_featured",
            "is_best_seller",
            "average_rating",
            "total_reviews",
            "meta_title",
            "meta_description",
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    product = serializers.SlugRelatedField(
        slug_field="slug", queryset=Product.objects.all()
    )

    class Meta:
        model = ProductReview
        fields = ["id", "user", "product", "rating", "comment", "created_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user or request.user.is_anonymous:
            return attrs

        user = request.user
        product = attrs.get("product")

        if not self.instance:
            if ProductReview.objects.filter(user=user, product=product).exists():
                raise serializers.ValidationError({
                    "non_field_errors": ["You have already reviewed this product."]
                })
        else:
            if product and product != self.instance.product:
                if ProductReview.objects.filter(user=user, product=product).exists():
                    raise serializers.ValidationError({
                        "non_field_errors": ["You have already reviewed this product."]
                    })

        return attrs
