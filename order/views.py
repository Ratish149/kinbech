from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from kinbech.utils.pagination import CustomPagination

from .filters import OrderFilter
from .models import Order, OrderItem
from .serializers import OrderDetailSerializer, OrderListSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    filterset_class = OrderFilter
    search_fields = ["order_id", "full_name", "phone_number"]
    ordering_fields = ["created_at", "total_amount"]
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method == "POST":
            return []  # Anyone can create an order (supports guest checkout)
        return [IsAuthenticated()]  # Only authenticated users can list orders

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderDetailSerializer
        return OrderListSerializer

    def get_queryset(self):
        user = self.request.user

        # Anonymous users cannot list orders
        if not user.is_authenticated:
            return Order.objects.none()

        # Optimize listing: select only the fields needed by OrderListSerializer
        # We do not prefetch items since they aren't displayed in the list view.
        queryset = Order.objects.only(
            "id",
            "order_id",
            "full_name",
            "phone_number",
            "total_amount",
            "payment_method",
            "status",
            "is_paid",
            "is_pos_order",
            "created_at",
        ).order_by("-created_at")

        if user.is_staff:
            return queryset
        return queryset.filter(user=user)


class OrderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderDetailSerializer
    lookup_field = "order_id"

    def get_queryset(self):
        user = self.request.user

        # Optimize detail view:
        # 1. prefetch_related('items') while selecting the 'product' for each item to avoid N+1 query.
        # 2. Use only() to load only fields required by the detail view.
        queryset = Order.objects.only(
            "id",
            "order_id",
            "user_id",
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
            "is_pos_order",
            "transaction_id",
            "tracking_number",
            "note",
            "created_at",
            "updated_at",
        ).prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("product").only(
                    "id",
                    "order_id",
                    "product_id",
                    "quantity",
                    "price",
                    "product__name",  # Needed for product_name ReadOnlyField in serializer
                    "product__thumbnail_image",  # Needed for product_image SerializerMethodField
                ),
            )
        )

        # Staff can access any order
        if user.is_authenticated and user.is_staff:
            return queryset

        # Registered users can access their own orders.
        # Anonymous users can access orders by order_id (tracking key for guest checkouts)
        return queryset

    def check_permissions(self, request):
        super().check_permissions(request)
        if request.method in ["PATCH", "DELETE"]:
            if not (request.user.is_staff):
                self.permission_denied(
                    request,
                    message="You do not have permission to modify or delete this order.",
                )
