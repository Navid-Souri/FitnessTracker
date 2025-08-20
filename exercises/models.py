from django.db import models
from accounts.models import User

class Exercise(models.Model):

    
    name = models.CharField(
        max_length=100,
        help_text="Name of the exercise"
    )
    category = models.TextField(
        blank=False,
        help_text="Type of exercise"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the exercise"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exercises'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Exercise'
        verbose_name_plural = 'Exercises'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category})"