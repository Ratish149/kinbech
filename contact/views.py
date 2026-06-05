from rest_framework import generics

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
    )
    serializer_class = ContactSerializer
    permission_classes = [IsAdminOrReadOnly]


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
    )
    serializer_class = ContactSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"
