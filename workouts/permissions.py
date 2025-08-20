from rest_framework import permissions


class IsSessionOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanLogExercise(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            session_id = request.data.get("session")
            if session_id:
                from .models import TrainingSession

                session = TrainingSession.objects.get(pk=session_id)
                return session.user == request.user
        return True
