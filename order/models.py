from django.conf import settings
from django.db import models

# Create your models here.


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("COD", "Cash on Delivery"),
        ("Esewa", "Esewa"),
        ("Khalti", "Khalti"),
        ("PhonePay", "PhonePay"),
    ]

    # User relationship (null=True allows guest checkouts)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    # Customer Info
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)

    # Structured Shipping Details
    shipping_address = models.TextField()
    order_id = models.CharField(max_length=100, unique=True, editable=False, blank=True)
    nearest_landmark = models.CharField(max_length=255, null=True, blank=True)

    # Financial breakdown
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Status & Payment
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="pending")
    is_paid = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    # Delivery Info
    tracking_number = models.CharField(max_length=100, null=True, blank=True)

    note = models.TextField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.full_name}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.order_id:
            import random
            import string

            # Generate a short unique code: e.g., KB-X9R2A
            while True:
                code = "KB-" + "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=5)
                )
                if not Order.objects.filter(order_id=code).exists():
                    self.order_id = code
                    break
            # Update only the order_id field to persist it without triggering signals recursively
            Order.objects.filter(pk=self.pk).update(order_id=self.order_id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
