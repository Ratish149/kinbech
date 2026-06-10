from django.db import transaction
from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image",
            "quantity",
            "price",
        ]

    def get_product_image(self, obj):
        request = self.context.get("request")
        if obj.product.thumbnail_image:
            if request:
                return request.build_absolute_uri(obj.product.thumbnail_image.url)
            return obj.product.thumbnail_image.url
        return None


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "order_id",
            "full_name",
            "phone_number",
            "total_amount",
            "payment_method",
            "status",
            "is_paid",
            "created_at",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_id",
            "user",
            "full_name",
            "phone_number",
            "email",
            "shipping_address",
            "nearest_landmark",
            "total_amount",
            "discount_amount",
            "payment_method",
            "status",
            "is_paid",
            "transaction_id",
            "tracking_number",
            "note",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["order_id", "created_at", "updated_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        with transaction.atomic():
            # Automatically assign the request user if authenticated
            request = self.context.get("request")
            if request and request.user and request.user.is_authenticated:
                validated_data["user"] = request.user

            order = Order.objects.create(**validated_data)

            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if items_data is not None:
                # For simplicity in updates, recreate the items.
                # This can be adjusted based on requirements.
                instance.items.all().delete()
                for item_data in items_data:
                    OrderItem.objects.create(order=instance, **item_data)

        return instance
