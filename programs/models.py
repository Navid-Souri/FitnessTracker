from django.db import models
from accounts.models import User
from exercises.models import Exercise

class ExerciseProgram(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="Name of the program"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the program"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='programs'
    )
    exercises = models.ManyToManyField(
        Exercise,
        through='ProgramExercise',
        related_name='programs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Exercise Program'
        verbose_name_plural = 'Exercise Programs'
        ordering = ['name']

    def __str__(self):
        return self.name

class ProgramExercise(models.Model):
    program = models.ForeignKey(
        ExerciseProgram,
        on_delete=models.CASCADE,
        related_name='program_exercises'
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='program_exercises'
    )
    default_sets = models.PositiveSmallIntegerField(
        default=3,
        help_text="Default number of sets"
    )
    default_reps = models.PositiveSmallIntegerField(
        default=10,
        help_text="Default number of repetitions"
    )
    default_rest_time = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Default rest time between sets in seconds"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Order in the program"
    )

    class Meta:
        verbose_name = 'Program Exercise'
        verbose_name_plural = 'Program Exercises'
        ordering = ['order']
        unique_together = ['program', 'exercise']

    def __str__(self):
        return f"{self.exercise.name} in {self.program.name}"