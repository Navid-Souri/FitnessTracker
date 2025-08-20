from rest_framework import permissions
from .models import ExerciseProgram


class IsProgramOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanAddExerciseToProgram(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            program_id = request.data.get("program")
            if program_id:
                program = ExerciseProgram.objects.get(pk=program_id)
                return program.user == request.user
        return True
