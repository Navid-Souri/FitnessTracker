# programs/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExerciseProgramViewSet, ProgramExerciseViewSet

router = DefaultRouter()
router.register(r'', ExerciseProgramViewSet, basename='program')
router.register(r'program-exercises', ProgramExerciseViewSet, basename='program-exercise')

urlpatterns = [
    path('', include(router.urls)),
]