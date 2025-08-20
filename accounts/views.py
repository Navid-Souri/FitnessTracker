from rest_framework import generics,permissions
from .models import Profile
from .serializers import ProfileSerializer
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .permissions import IsOwner, IsCurrentProfileOwner
from .serializers import UserRegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer


class ProfileHistoryView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        user = self.request.user
        return Profile.objects.filter(user=user).order_by("-created_at")


class CurrentProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = ProfileSerializer
    permission_classes = [IsCurrentProfileOwner]

    # This method is used to get the current profile of the user
    def get_object(self):
        return get_object_or_404(
            Profile.objects.filter(user=self.request.user), is_current=True
        )

    def perform_update(self, serializer):

        old_profile = self.get_object()
        old_profile.is_current = False
        old_profile.save()

        new_profile = serializer.save(
            user=self.request.user, is_current=True, created_at=timezone.now()
        )
        return new_profile


class CreateProfileView(generics.CreateAPIView):
    

    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # فقط کاربران لاگین‌شده

    def perform_create(self, serializer):
        
        Profile.objects.filter(user=self.request.user, is_current=True).update(
            is_current=False
        )

        
        serializer.save(
            user=self.request.user, is_current=True, created_at=timezone.now()
        )
