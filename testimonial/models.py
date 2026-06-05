from django.db import models


# Create your models here.
class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
