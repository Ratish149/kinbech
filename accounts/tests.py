from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AccountsAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse("user-register")
        self.login_url = reverse("user-login")
        self.refresh_url = reverse("token-refresh")
        self.profile_url = reverse("user-profile")

        self.user_data = {
            "email": "testuser@example.com",
            "phone_number": "9876543210",
            "password": "securepassword123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "username" not in response.data
        assert response.data["email"] == "testuser@example.com"
        assert response.data["phone_number"] == "9876543210"
        assert "password" not in response.data

        # Check that user is created in database and username is set to email
        user = User.objects.get(email="testuser@example.com")
        assert user.username == "testuser@example.com"

    def test_user_registration_duplicate_email(self):
        self.client.post(self.register_url, self.user_data, format="json")
        duplicate_data = self.user_data.copy()
        duplicate_data["phone_number"] = "1111111111"
        response = self.client.post(self.register_url, duplicate_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_user_login(self):
        # First register user
        self.client.post(self.register_url, self.user_data, format="json")

        # Now login
        login_data = {"email": "testuser@example.com", "password": "securepassword123"}
        response = self.client.post(self.login_url, login_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["username"] == "testuser@example.com"
        assert response.data["user"]["phone_number"] == "9876543210"

    def test_user_profile(self):
        # Register and login to get access token
        self.client.post(self.register_url, self.user_data, format="json")
        login_data = {"email": "testuser@example.com", "password": "securepassword123"}
        login_response = self.client.post(self.login_url, login_data, format="json")
        access_token = login_response.data["access"]

        # Call profile URL without token
        response = self.client.get(self.profile_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Call profile URL with token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.profile_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser@example.com"
        assert response.data["phone_number"] == "9876543210"
