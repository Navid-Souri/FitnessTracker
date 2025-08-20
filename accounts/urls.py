from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ProfileHistoryView,
    CurrentProfileView,
    CreateProfileView,
    RegisterView,
)
from django.urls import path

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("register/", RegisterView.as_view(), name="register"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/history/", ProfileHistoryView.as_view(), name="profile_history"),
    path("profile/current/", CurrentProfileView.as_view(), name="current_profile"),
    path("profile/create/", CreateProfileView.as_view(), name="create_profile"),
]
