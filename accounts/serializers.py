from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "is_staff",
        )
        read_only_fields = ("id", "username", "email", "is_staff")



class POSCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "phone_number")

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "phone_number",
            "password",
            "first_name",
            "last_name",
        )

    def validate_email(self, value):
        phone_number = self.initial_data.get("phone_number")
        queryset = User.objects.filter(email=value)
        if phone_number:
            queryset = queryset.exclude(phone_number=phone_number)
        if queryset.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        try:
            existing_user = User.objects.get(phone_number=value)
            if existing_user.has_usable_password():
                raise serializers.ValidationError(
                    "A user with this phone number already exists."
                )
        except User.DoesNotExist:
            pass
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        phone_number = validated_data["phone_number"]
        password = validated_data["password"]
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")

        existing_user = User.objects.filter(phone_number=phone_number).first()
        if existing_user and not existing_user.has_usable_password():
            existing_user.username = email
            existing_user.email = email
            existing_user.set_password(password)
            existing_user.first_name = first_name
            existing_user.last_name = last_name
            existing_user.save()
            return existing_user

        user = User.objects.create_user(
            username=email,
            email=email,
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        return user



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the default username field from the serializer
        self.fields.pop(self.username_field, None)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to access token
        token["username"] = user.username
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["phone_number"] = user.phone_number
        token["email"] = user.email
        token["is_staff"] = user.is_staff
        return token

    def validate(self, attrs):
        email = attrs.get("email")

        # Look up the user by email to get their actual username for authentication
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            username = email

        attrs[self.username_field] = username
        data = super().validate(attrs)

        # Add user details to response
        return data
