from rest_framework import serializers
from .models import Exercise


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ["id", "name", "category"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """Auto-assign the current user when creating exercises"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        user = self.context["request"].user
        name = data.get("name")
        category = data.get("category")
        if Exercise.objects.filter(user=user, name=name, category=category).exists():
            raise serializers.ValidationError(
                "This exercise already exists for this user and category."
            )
        return data

    def update(self, instance, validated_data):
        # "instance" representing a single record in a database table
        instance.name = validated_data.get("name", instance.name)
        instance.category = validated_data.get("category", instance.category)
        instance.save()
        return instance
