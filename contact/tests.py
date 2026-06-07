from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Contact

User = get_user_model()


class ContactAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            phone_number="9876543210",
        )
        self.contact_data = {
            "name": "Ratish",
            "phone_number": "9876543210",
            "email": "ratish@example.com",
            "subject": "Hello",
            "message": "Hi, I have a question.",
        }

    def test_create_contact_unauthenticated(self):
        url = reverse("contact-list")
        response = self.client.post(url, self.contact_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Contact.objects.first().name, "Ratish")

    def test_list_contacts_unauthenticated(self):
        url = reverse("contact-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_contacts_authenticated(self):
        Contact.objects.create(**self.contact_data)
        self.client.force_authenticate(user=self.user)
        url = reverse("contact-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
