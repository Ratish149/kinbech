from rest_framework import serializers

from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "name",
            "phone_number",
            "email",
            "subject",
            "message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
