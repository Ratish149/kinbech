from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CustomTokenObtainPairSerializer,
    POSCustomerSerializer,
    UserDetailSerializer,
    UserRegisterSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CustomerListCreateView(generics.ListCreateAPIView):
    serializer_class = POSCustomerSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = User.objects.filter(is_staff=False)
        phone_number = self.request.query_params.get("phone_number")
        if phone_number:
            queryset = queryset.filter(phone_number__icontains=phone_number)
        return queryset

    def perform_create(self, serializer):
        phone_number = serializer.validated_data.get("phone_number")
        user = serializer.save(username=phone_number)
        user.set_unusable_password()
        user.save()
