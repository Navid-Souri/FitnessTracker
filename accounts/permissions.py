from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsCurrentProfileOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ["PUT", "PATCH", "DELETE"]:
            profile = view.get_object()
            return profile.user == request.user
        return True
