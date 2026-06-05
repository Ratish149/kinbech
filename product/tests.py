from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product, ProductReview, Subcategory

User = get_user_model()


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fresh Meat", slug="fresh-meat")
        self.subcategory = Subcategory.objects.create(
            category=self.category, name="Mutton", slug="mutton"
        )
        self.product = Product.objects.create(
            name="Fresh Mutton Curry Cut",
            slug="fresh-mutton-curry-cut",
            category=self.category,
            subcategory=self.subcategory,
            price=1450.00,
            unit="1 kg",
            stock=30,
        )

    def test_model_str_representations(self):
        assert str(self.category) == "Fresh Meat"
        assert str(self.subcategory) == "Fresh Meat -> Mutton"
        assert str(self.product) == "Fresh Mutton Curry Cut"


class ProductReviewAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            phone_number="9876543210",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="testpassword",
            phone_number="9876543211",
        )
        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword",
            phone_number="9876543212",
        )

        self.category = Category.objects.create(name="Beverages", slug="beverages")
        self.subcategory = Subcategory.objects.create(
            category=self.category, name="Tea", slug="tea"
        )
        self.product = Product.objects.create(
            name="Green Tea",
            slug="green-tea",
            category=self.category,
            subcategory=self.subcategory,
            price=150.00,
            unit="1 pack",
            stock=10,
        )
        self.product2 = Product.objects.create(
            name="Black Tea",
            slug="black-tea",
            category=self.category,
            subcategory=self.subcategory,
            price=120.00,
            unit="1 pack",
            stock=20,
        )

    def test_list_reviews(self):
        ProductReview.objects.create(
            user=self.user, product=self.product, rating=5, comment="Excellent!"
        )
        ProductReview.objects.create(
            user=self.other_user, product=self.product, rating=4, comment="Good"
        )

        url = reverse("review-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

    def test_create_review_unauthenticated(self):
        url = reverse("review-list-create")
        data = {"product": self.product.slug, "rating": 5, "comment": "Superb!"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("review-list-create")
        data = {"product": self.product.slug, "rating": 5, "comment": "Superb!"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["user"], self.user.username)
        self.assertEqual(response.data["comment"], "Superb!")
        self.assertEqual(ProductReview.objects.count(), 1)

    def test_create_duplicate_review(self):
        ProductReview.objects.create(
            user=self.user, product=self.product, rating=5, comment="First review"
        )

        self.client.force_authenticate(user=self.user)
        url = reverse("review-list-create")
        data = {
            "product": self.product.slug,
            "rating": 4,
            "comment": "Second review attempt",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_create_review_invalid_rating(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("review-list-create")
        data = {"product": self.product.slug, "rating": 6, "comment": "Too high!"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rating"] = 0
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_reviews(self):
        review1 = ProductReview.objects.create(
            user=self.user, product=self.product, rating=5, comment="Love it!"
        )
        review2 = ProductReview.objects.create(
            user=self.other_user, product=self.product2, rating=3, comment="Okay"
        )

        url = reverse("review-list-create")
        response = self.client.get(url, {"product": self.product.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], review1.id)

        response = self.client.get(url, {"user": self.other_user.username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], review2.id)

    def test_retrieve_review(self):
        review = ProductReview.objects.create(
            user=self.user, product=self.product, rating=5, comment="Love it!"
        )
        url = reverse("review-detail", kwargs={"pk": review.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["comment"], "Love it!")

    def test_update_review_owner(self):
        review = ProductReview.objects.create(
            user=self.user, product=self.product, rating=5, comment="Love it!"
        )
        self.client.force_authenticate(user=self.user)
        url = reverse("review-detail", kwargs={"pk": review.pk})
        data = {
            "product": self.product.slug,
            "rating": 4,
            "comment": "Actually, it's just okay.",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 4)
        self.assertEqual(response.data["comment"], "Actually, it's just okay.")

    def test_update_review_non_owner(self):
        review = ProductReview.objects.create(
            user=self.user, product=self.product, rating=5, comment="Love it!"
        )
        self.client.force_authenticate(user=self.other_user)
        url = reverse("review-detail", kwargs={"pk": review.pk})
        data = {
            "product": self.product.slug,
            "rating": 4,
            "comment": "Trying to modify",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_owner(self):
        review = ProductReview.objects.create(
            user=self.user, product=self.product, rating=5, comment="Love it!"
        )
        self.client.force_authenticate(user=self.user)
        url = reverse("review-detail", kwargs={"pk": review.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProductReview.objects.count(), 0)

    def test_delete_review_non_owner(self):
        review = ProductReview.objects.create(
            user=self.user, product=self.product, rating=5, comment="Love it!"
        )
        self.client.force_authenticate(user=self.other_user)
        url = reverse("review-detail", kwargs={"pk": review.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ProductReview.objects.count(), 1)
