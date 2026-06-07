from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from kinbech.utils.pagination import CustomPagination
from kinbech.utils.permissions import IsAdminOrReadOnly

from .models import Contact
from .serializers import ContactSerializer

# Create your views here.


class ContactListCreateView(generics.ListCreateAPIView):
    queryset = Contact.objects.only(
        "id",
        "name",
        "phone_number",
        "email",
        "subject",
        "message",
        "created_at",
        "updated_at",
    ).order_by("-created_at")
    serializer_class = ContactSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [AllowAny()]


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.only(
        "id",
        "name",
        "phone_number",
        "email",
        "subject",
        "message",
        "created_at",
        "updated_at",
    ).order_by("-created_at")
    serializer_class = ContactSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"
