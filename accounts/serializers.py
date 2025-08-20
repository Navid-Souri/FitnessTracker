from rest_framework import serializers
from .models import Profile
from django.contrib.auth import get_user_model


User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    bmi = serializers.SerializerMethodField()  # Removed incorrect 'source' parameter

    class Meta:
        model = Profile
        fields = [
            "is_current",
            "created_at",
            "weight",
            "bmi",
            "height",
            "location",
            "birth_date",
        ]
        read_only_fields = ["created_at", "bmi"]

    def get_bmi(self, obj):
        """Calculate BMI from weight (kg) and height (cm)"""
        if obj.weight and obj.height:
            height_in_meters = obj.height / 100
            return round(obj.weight / (height_in_meters**2), 1)  # Rounded to 1 decimal
        return None
