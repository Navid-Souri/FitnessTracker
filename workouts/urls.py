# workouts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrainingSessionViewSet, WorkoutLogViewSet

router = DefaultRouter()
router.register(r'sessions', TrainingSessionViewSet, basename='session')
router.register(r'logs', WorkoutLogViewSet, basename='log')

urlpatterns = [
    path('', include(router.urls)),
]