from django.db import models
from django.conf import settings

class Complaint(models.Model):
    """Complaint model with ward selection"""
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]
    
    CATEGORY_CHOICES = [
        ('Road Maintenance', 'Road Maintenance'),
        ('Street Light', 'Street Light'),
        ('Water Supply', 'Water Supply'),
        ('Sanitation', 'Sanitation'),
        ('Traffic', 'Traffic'),
        ('Parks', 'Parks & Recreation'),
        ('Other', 'Other'),
    ]
    
    # Ward choices (1-15)
    WARD_CHOICES = [(str(i), f'Ward {i}') for i in range(1, 16)]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='complaints'
    )
    ward = models.CharField(
        max_length=2, 
        choices=WARD_CHOICES,
        help_text="Select your ward number (1-15)"
    )
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField()
    image = models.ImageField(upload_to='complaints/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Ward {self.ward} - {self.category} - {self.user.fullname}"
    
    class Meta:
        db_table = 'complaints'
        ordering = ['-created_at']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['ward', 'status']),
        ]