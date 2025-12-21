from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from complaints.models import Complaint

class Feedback(models.Model):
    """Feedback model"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='feedbacks'
    )
    complaint = models.ForeignKey(
        Complaint, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='feedbacks'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback by {self.user.fullname} - {self.rating}★"
    
    def get_star_display(self):
        return '⭐' * self.rating
    
    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'