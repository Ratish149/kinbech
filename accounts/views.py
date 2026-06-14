from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    AdminCustomerSerializer,
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
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return POSCustomerSerializer
        return AdminCustomerSerializer

    def get_queryset(self):
        from django.db.models import Count, DecimalField, Sum
        from django.db.models.functions import Coalesce

        queryset = (
            User.objects
            .filter(is_staff=False)
            .annotate(
                total_orders=Count("orders", distinct=True),
                total_spent=Coalesce(
                    Sum("orders__total_amount"),
                    0.0,
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
            )
            .order_by("-date_joined")
        )

        search = self.request.query_params.get("search")
        if search:
            from django.db.models import Q

            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(email__icontains=search)
            )

        phone_number = self.request.query_params.get("phone_number")
        if phone_number:
            queryset = queryset.filter(phone_number__icontains=phone_number)

        return queryset

    def perform_create(self, serializer):
        phone_number = serializer.validated_data.get("phone_number")
        user = serializer.save(username=phone_number)
        user.set_unusable_password()
        user.save()


class CustomerDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AdminCustomerSerializer

    def get_queryset(self):
        from django.db.models import Count, DecimalField, Sum
        from django.db.models.functions import Coalesce

        return User.objects.filter(is_staff=False).annotate(
            total_orders=Count("orders", distinct=True),
            total_spent=Coalesce(
                Sum("orders__total_amount"),
                0.0,
                output_field=DecimalField(max_digits=10, decimal_places=2),
            ),
        )
