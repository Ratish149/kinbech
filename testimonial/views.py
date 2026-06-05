from rest_framework import generics

from kinbech.utils.permissions import IsAdminOrReadOnly

from .models import Testimonial
from .serializers import TestimonialSerializer


class TestimonialListCreateView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.only(
        "id", "name", "rating", "description", "created_at", "updated_at"
    )
    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminOrReadOnly]


class TestimonialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.only(
        "id", "name", "rating", "description", "created_at", "updated_at"
    )
    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"
