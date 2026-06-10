from django.urls import path

from .views import OrderDetailAPIView, OrderListCreateView

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<str:order_id>/", OrderDetailAPIView.as_view(), name="order-detail"),
]
