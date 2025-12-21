from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom User model for citizens"""
    
    # Ward choices (1-15)
    WARD_CHOICES = [(str(i), f'Ward {i}') for i in range(1, 16)]
    
    fullname = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    ward = models.CharField(
        max_length=2, 
        choices=WARD_CHOICES,
        blank=True,
        null=True,
        help_text="Your ward number (1-15)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.fullname
    
    class Meta:
        db_table = 'users'