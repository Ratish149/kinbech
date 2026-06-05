from django.urls import path

from .views import ContactDetailView, ContactListCreateView

urlpatterns = [
    path("contacts/", ContactListCreateView.as_view(), name="contact-list"),
    path(
        "contacts/<int:pk>/",
        ContactDetailView.as_view(),
        name="contact-detail",
    ),
]
