from .models import Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Max, Min, Sum, Count
from datetime import timedelta
from workouts.models import WorkoutLog
from exercises.models import Exercise
from django.utils import timezone


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

        # Calculate BMI for each profile
        def calculate_bmi(profile):
            if profile.height and profile.weight:
                height_in_meters = profile.height / 100  # Convert cm to meters
                return round(profile.weight / (height_in_meters**2), 1)
            return None

        return Response(
            {
                "time_period": f"Last {days} days",
                "current": calculate_bmi(profiles.last()),
                "history": [
                    {"date": p.created_at.date(), "value": calculate_bmi(p)}
                    for p in profiles
                    if calculate_bmi(p) is not None  # Only include valid BMI values
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

        # Calculate total volume
        total_volume = 0
        for log in logs:
            total_volume += (log.sets or 0) * (log.reps or 0) 
        
        volume_data = {
            "total_volume": total_volume,
            "sessions_per_week": round(logs.count() / (days / 7), 1) if days > 0 else 0,
        }

        session_count = logs.values("session").distinct().count()
        frequency_data = {
            "total_sessions": session_count,
            "sessions_per_week": round(session_count / (days / 7), 1) if days > 0 else 0,
        }

        # Progressive overload tracking
        progression = []
        for log in logs.order_by("session__date"):
            volume = (log.weight or 0)
            progression.append({
                "session__date": log.session.date.isoformat(),
                "volume": volume
            })

        return Response(
            {
                "exercise": exercise.name,
                "time_period": f"Last {days} days",
                "volume": volume_data,
                "frequency": frequency_data,
                "progression": progression,
                "last_improvement": self._get_improvement(logs),
            }
        )

    def _get_improvement(self, logs):
        """Calculate percentage improvement over period"""
        if logs.count() < 2:
            return None

        sorted_logs = logs.order_by("session__date")
        first = sorted_logs.first()
        last = sorted_logs.last()
        
        first_vol = (first.sets or 0) * (first.reps or 0) * (first.weight or 1)
        last_vol = (last.sets or 0) * (last.reps or 0) * (last.weight or 1)

        if first_vol == 0:  # Avoid division by zero
            return None

        improvement_percentage = round((last_vol - first_vol) / first_vol * 100, 1)
        time_span_days = (last.session.date - first.session.date).days

        return {
            "percentage": improvement_percentage,
            "time_span": time_span_days,
            "first_volume": first_vol,
            "last_volume": last_vol,
            "first_date": first.session.date.isoformat(),
            "last_date": last.session.date.isoformat(),
        }