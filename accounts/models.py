from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = models.CharField(
        max_length=15,
        unique=True,
        validators=[MinLengthValidator(4)],
        help_text="Required. 4-15 characters. Letters, digits and @/./+/-/_ only."
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        help_text="Required. Please provide a valid email address."
    )
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active."
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site."
    )
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username
    
    
    

class Profile(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='profiles'
    )
    height = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Height in centimeters"
    )
    weight = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Weight in kilograms"
    )
    location = models.CharField(
        max_length=30,
        blank=True,
        help_text="Your current location"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        help_text="Format: YYYY-MM-DD"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(
        default=False,
        help_text="Mark if this is the current profile"
    )

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_current'],
                condition=models.Q(is_current=True),
                name='unique_current_profile'
            )
        ]

    def save(self, *args, **kwargs):
    
        if self.is_current:
            Profile.objects.filter(user=self.user, is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Current" if self.is_current else "Historical"
        return f"{status} profile for {self.user.username} ({self.created_at.date()})"