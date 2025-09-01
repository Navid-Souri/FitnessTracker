from rest_framework import serializers
from .models import TrainingSession, WorkoutLog
from programs.models import ExerciseProgram
from accounts.models import User
from exercises.models import Exercise


class TrainingSessionSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source="program.name", read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = TrainingSession
        fields = [
            "user",
            "date",
            "created_at",
            "program",
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
            "id",
            "session_id",
            "exercise",  # Add this line
            "exercise_name",
            "sets",
            "reps",
            "weight",
            "rest_time",
            "volume",
            "notes",
        ]
        read_only_fields = ["id", "volume", "exercise"]  # Make 'exercise' read-only

    def get_volume(self, obj):
        return obj.sets * obj.reps * obj.weight

    def get_notes(self, obj):
        return obj.notes if obj.notes else ""



class WorkoutLogCreateUpdateSerializer(serializers.ModelSerializer):
    exercise = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(), required=True
    )
    session = serializers.PrimaryKeyRelatedField(
        queryset=TrainingSession.objects.all(), required=True
    )

    class Meta:
        model = WorkoutLog
        fields = ["session", "exercise", "sets", "reps", "weight", "rest_time", "notes"]
        extra_kwargs = {
            "rest_time": {"required": False, "allow_null": True},
            "notes": {"required": False, "allow_null": True},
        }

    def validate(self, data):
        session_user = data["session"].user
        exercise_user = data["exercise"].user

        if session_user != exercise_user:
            raise serializers.ValidationError(
                "You can only log exercises for your own sessions."
            )
        return data

    def to_internal_value(self, data):
        # Handle empty strings for optional fields
        if "rest_time" in data and data["rest_time"] == "":
            data["rest_time"] = None
        if "notes" in data and data["notes"] == "":
            data["notes"] = None
        return super().to_internal_value(data)
