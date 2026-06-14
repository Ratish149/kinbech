from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomerDetailAPIView,
    CustomerListCreateView,
    CustomTokenObtainPairView,
    RegisterView,
    UserProfileView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="user-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", UserProfileView.as_view(), name="user-profile"),
    path("customers/", CustomerListCreateView.as_view(), name="admin-customer-list-create"),
    path("customers/<int:pk>/", CustomerDetailAPIView.as_view(), name="admin-customer-detail"),
]
