from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    LANGUAGE_CHOICES = [
        ('ne', 'Nepali'),
        ('en', 'English'),
    ]
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    is_citizen = models.BooleanField(default=True)
    preferred_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='ne')
    
    def __str__(self):
        return f"{self.username} ({self.district or 'No District'})"