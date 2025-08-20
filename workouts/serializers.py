from rest_framework import serializers
from .models import TrainingSession, WorkoutLog
from programs.models import ExerciseProgram
from accounts.models import User


class TrainingSessionSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source="program.name", read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = TrainingSession
        fields = [
            "user",
            "date",
            "created_at",
            "program_name",
            "duration",
            "notes",
            "id",
        ]
        read_only_fields = ["id", "program_name", "user"]

    def create(self, validated_data):
        if "user" not in validated_data:
            validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class WorkoutLogSerializer(serializers.ModelSerializer):

    session_id = serializers.CharField(source="session.id", read_only=True)
    exercise_name = serializers.CharField(source="exercise.name", read_only=True)
    volume = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutLog
        fields = [
            "session_id",
            "exercise_name",
            "sets",
            "reps",
            "weight",
            "rest_time",
            "volume",
            "notes",
        ]

    def get_volume(self, obj):
        return obj.sets * obj.reps * obj.weight

    def get_notes(self, obj):
        return obj.notes


class WorkoutLogCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutLog
        fields = ["session", "exercise", "sets", "reps", "weight", "rest_time", "notes"]

    def validate(self, data):
        session_user = data["session"].user
        exercise_user = data["exercise"].user

        if session_user != exercise_user:
            raise serializers.ValidationError(
                "You can only log exercises for your own sessions."
            )
        return data
