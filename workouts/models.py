from django.db import models
from accounts.models import User
from programs.models import ExerciseProgram, Exercise

class TrainingSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='training_sessions'
    )
    program = models.ForeignKey(
        ExerciseProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_sessions'
    )
    date = models.DateField(help_text="Date of the training session")
    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the session"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Training Session'
        verbose_name_plural = 'Training Sessions'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username}'s session on {self.date}"

class WorkoutLog(models.Model):
    session = models.ForeignKey(
        TrainingSession,
        on_delete=models.CASCADE,
        related_name='workout_logs'
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='workout_logs'
    )
    sets = models.PositiveSmallIntegerField(help_text="Number of sets performed")
    reps = models.PositiveSmallIntegerField(help_text="Number of repetitions per set")
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight used in kg"
    )
    rest_time = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Rest time between sets in seconds"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this exercise"
    )

    class Meta:
        verbose_name = 'Workout Log'
        verbose_name_plural = 'Workout Logs'
        ordering = ['session', 'id']

    def __str__(self):
        return f"{self.exercise.name} in session {self.session.id}"