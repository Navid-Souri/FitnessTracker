from rest_framework import permissions

class IsSessionOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # For TrainingSession objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # For WorkoutLog objects - check through session
        elif hasattr(obj, 'session'):
            return obj.session.user == request.user
        return False

class CanLogExercise(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            session_id = request.data.get("session")
            if session_id:
                from .models import TrainingSession
                try:
                    session = TrainingSession.objects.get(pk=session_id)
                    return session.user == request.user
                except TrainingSession.DoesNotExist:
                    return False
        return True