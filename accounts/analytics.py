from .models import Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Max, Min, Sum, Count
from datetime import timedelta, timezone
from workouts.models import WorkoutLog
from exercises.models import Exercise


class BaseAnalyticsView(APIView):

    DEFAULT_DAYS = 30

    def get_time_range(self, request):
        days = int(request.query_params.get("days", self.DEFAULT_DAYS))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date, days


class WeightAnalyticsView(BaseAnalyticsView):
    def get(self, request):
        start_date, end_date, days = self.get_time_range(request)

        profiles = Profile.objects.filter(
            user=request.user, created_at__range=[start_date, end_date]
        ).order_by("created_at")

        if not profiles.exists():
            return Response({"message": "No profile data available"}, status=404)

        return Response(
            {
                "time_period": f"Last {days} days",
                "current": profiles.last().weight,
                "stats": profiles.aggregate(
                    avg=Avg("weight"), max=Max("weight"), min=Min("weight")
                ),
                "history": [
                    {"date": p.created_at.date(), "value": p.weight} for p in profiles
                ],
            }
        )


class BMIAnalyticsView(BaseAnalyticsView):
    def get(self, request):
        start_date, end_date, days = self.get_time_range(request)

        profiles = Profile.objects.filter(
            user=request.user, created_at__range=[start_date, end_date]
        ).order_by("created_at")

        if not profiles.exists():
            return Response({"message": "No profile data available"}, status=404)

        return Response(
            {
                "time_period": f"Last {days} days",
                "current": profiles.last().bmi(),
                "history": [
                    {"date": p.created_at.date(), "value": p.bmi()} for p in profiles
                ],
            }
        )


class ExerciseAnalyticsView(BaseAnalyticsView):  
    def get(self, request, exercise_id):
        start_date, end_date, days = self.get_time_range(request)

        try:
            exercise = Exercise.objects.get(id=exercise_id, user=request.user)
        except Exercise.DoesNotExist:
            return Response({"error": "Exercise not found"}, status=404)

        logs = WorkoutLog.objects.filter(
            exercise=exercise,
            session__user=request.user,
            session__date__range=[start_date, end_date],
        ).select_related("session")

        
        volume_data = logs.aggregate(
            total_volume=Sum("sets" * "reps"),
            volume_per_week=Sum("sets" * "reps") / (days / 7),
            best_session=Max("sets" * "reps" ),
        )

        
        session_count = logs.values("session").distinct().count()
        frequency_data = {
            "total_sessions": session_count,
            "sessions_per_week": round(session_count / (days / 7), 1),
            "total_workouts": logs.count(),
        }

        # Progressive overload tracking
        progression = logs.order_by("session__date").values(
            "session__date", volume=Sum("sets" * "reps" * "weight")
        )

        return Response(
            {
                "exercise": exercise.name,
                "time_period": f"Last {days} days",
                "volume": {**volume_data, "unit": "kg"},  # Add unit for clarity
                "frequency": frequency_data,
                "progression": list(progression),
                "last_improvement": self._get_improvement(logs),
            }
        )

    def _get_improvement(self, logs):
        """Calculate percentage improvement over period"""
        if logs.count() < 2:
            return None

        first = logs.earliest("session__date")
        last = logs.latest("session__date")
        first_vol = first.sets * first.reps * (first.weight or 1)
        last_vol = last.sets * last.reps * (last.weight or 1)

        return {
            "percentage": round((last_vol - first_vol) / first_vol * 100, 1),
            "time_span": (last.session.date - first.session.date).days,
        }
