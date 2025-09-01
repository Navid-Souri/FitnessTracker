from rest_framework import viewsets
from .serializers import (
    WorkoutLogCreateUpdateSerializer,
    WorkoutLogSerializer,
    TrainingSessionSerializer,
)
from .models import WorkoutLog, TrainingSession
from .permissions import IsSessionOwner, CanLogExercise
from programs.serializers import ProgramExerciseReadSerializer
from programs.models import ProgramExercise
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class WorkoutLogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSessionOwner, CanLogExercise]

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

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            # Handle null values properly
            data = serializer.validated_data
            if "rest_time" in data and data["rest_time"] is None:
                data["rest_time"] = 0
            if "notes" in data and data["notes"] is None:
                data["notes"] = ""

            self.perform_update(serializer)

            # Return the updated data with read serializer
            read_serializer = WorkoutLogSerializer(instance)
            return Response(read_serializer.data)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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

    @action(detail=True, methods=["get"])
    def program_exercises(self, request, pk=None):
        """Get all exercises for the program linked to this session"""
        try:
            session = self.get_object()
            if not session.program:
                return Response(
                    {"detail": "This session is not linked to a program."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            program_exercises = (
                ProgramExercise.objects.filter(program=session.program)
                .select_related("exercise")
                .order_by("order")
            )

            serializer = ProgramExerciseReadSerializer(program_exercises, many=True)
            return Response(serializer.data)

        except TrainingSession.DoesNotExist:
            return Response(
                {"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["post"])
    def create_program_logs(self, request, pk=None):
        """Automatically create workout logs for all exercises in the program"""
        try:
            session = self.get_object()

            if not session.program:
                return Response(
                    {"detail": "This session is not linked to a program."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get all exercises from the program
            program_exercises = ProgramExercise.objects.filter(
                program=session.program
            ).select_related("exercise")

            created_logs = []

            # Create workout log for each exercise
            for program_exercise in program_exercises:
                workout_log = WorkoutLog.objects.create(
                    session=session,
                    exercise=program_exercise.exercise,
                    sets=program_exercise.default_sets or 3,  # Default values
                    reps=program_exercise.default_reps or 10,
                    weight=0,  # User will fill this in
                    rest_time=program_exercise.default_rest_time or 60,
                    notes=f"Auto-created from program: {session.program.name}",
                )
                created_logs.append(
                    {
                        "id": workout_log.id,
                        "exercise": workout_log.exercise.name,
                        "sets": workout_log.sets,
                        "reps": workout_log.reps,
                        "weight": workout_log.weight,
                        "rest_time": workout_log.rest_time,
                    }
                )

            return Response(
                {
                    "detail": f"Created {len(created_logs)} workout logs",
                    "logs": created_logs,
                },
                status=status.HTTP_201_CREATED,
            )

        except TrainingSession.DoesNotExist:
            return Response(
                {"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND
            )
