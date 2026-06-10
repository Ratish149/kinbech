from django.urls import path

from .views import (
    AlertsAPIView,
    CategoryChartAPIView,
    DashboardStatsAPIView,
    SalesChartAPIView,
)

urlpatterns = [
    path("dashboard/", DashboardStatsAPIView.as_view(), name="dashboard-stats"),
    path("sales-chart/", SalesChartAPIView.as_view(), name="sales-chart"),
    path("category-chart/", CategoryChartAPIView.as_view(), name="category-chart"),
    path("alerts/", AlertsAPIView.as_view(), name="alerts"),
]
