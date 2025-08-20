from django.shortcuts import render
from rest_framework import viewsets, mixins
from .models import ExerciseProgram, ProgramExercise
from .serializers import (
    ExerciseProgramSerializer,
    ProgramExerciseReadSerializer,
    ProgramExerciseWriteSerializer,
)
from .permissions import IsProgramOwner, CanAddExerciseToProgram
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status


class ExerciseProgramViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseProgramSerializer
    queryset = ExerciseProgram.objects.all()
    permission_classes = [IsAuthenticated, IsProgramOwner]

    def get_queryset(self):
        return ExerciseProgram.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProgramExerciseViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    permission_classes = [IsProgramOwner, CanAddExerciseToProgram]
    queryset = ProgramExercise.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["POST", "PATCH", "PUT"]:
            return ProgramExerciseWriteSerializer
        return ProgramExerciseReadSerializer

    # give exercise with equal program_id
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(program__user=self.request.user)

        program_id = self.request.query_params.get("program_id")
        if program_id:
            queryset = queryset.filter(program_id=program_id)
        return queryset.select_related("program", "exercise").order_by("order")

    def perform_create(self, serializer):
        program = serializer.validated_data["program"]
        if program.user != self.request.user:
            raise PermissionDenied("شما مجوز اضافه کردن تمرین به این برنامه را ندارید")
        serializer.save()

    def handle_exception(self, exc):
        if isinstance(exc, ProgramExercise.DoesNotExist):
            return Response(
                {"detail": "برنامه یا تمرین مورد نظر یافت نشد"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return super().handle_exception(exc)
