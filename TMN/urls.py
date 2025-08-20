from django.contrib import admin
from django.urls import path , include
from accounts.analytics import WeightAnalyticsView, BMIAnalyticsView , ExerciseAnalyticsView
from accounts import urls as accounts


urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/exercises/', include('exercises.urls')),
    path('api/programs/', include('programs.urls')),
    path('api/workouts/', include('workouts.urls')),
    path('api/analytics/weight/', WeightAnalyticsView.as_view()),
    path('api/analytics/bmi/', BMIAnalyticsView.as_view()),
    path('api/analytics/exercise/<int:exercise_id>/', ExerciseAnalyticsView.as_view()),
]
