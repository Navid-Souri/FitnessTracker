from rest_framework import viewsets
from .serializers import (
    WorkoutLogCreateUpdateSerializer,
    WorkoutLogSerializer,
    TrainingSessionSerializer,
)
from .models import WorkoutLog, TrainingSession
from .permissions import IsSessionOwner, CanLogExercise


class WorkoutLogViewSet(viewsets.ModelViewSet):
    permission_classes = [CanLogExercise, IsSessionOwner]

    def get_serializer_class(self):
        if self.request.method in ["POST", "PATCH", "PUT"]:
            return WorkoutLogCreateUpdateSerializer
        return WorkoutLogSerializer

    def get_queryset(self):
        queryset = WorkoutLog.objects.filter(
            session__user=self.request.user
        ).select_related("session", "exercise")
        session_id = self.request.query_params.get("session_id")
        exercise_id = self.request.query_params.get("exercise_id")
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        if exercise_id:
            queryset = queryset.filter(exercise_id=exercise_id)

        return queryset.order_by("session__date", "id")


class TrainingSessionViewSet(viewsets.ModelViewSet):
    serializer_class = TrainingSessionSerializer
    permission_classes = [IsSessionOwner]

    def get_queryset(self):
        queryset = TrainingSession.objects.filter(user=self.request.user)
        program_id = self.request.query_params.get("program_id")
        if program_id:
            queryset = queryset.filter(program_id=program_id)

        return queryset.order_by("-date", "-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
