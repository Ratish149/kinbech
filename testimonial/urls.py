from django.urls import path

from .views import TestimonialDetailView, TestimonialListCreateView

urlpatterns = [
    path("testimonials/", TestimonialListCreateView.as_view(), name="testimonial-list"),
    path(
        "testimonials/<int:pk>/",
        TestimonialDetailView.as_view(),
        name="testimonial-detail",
    ),
]
