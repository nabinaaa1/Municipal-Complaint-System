from django.db import models
from django.conf import settings
import uuid
import os
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from datetime import timedelta

def complaint_image_path(instance, filename):
    """Generate unique filename using UUID"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('complaints', filename)

class Complaint(models.Model):
    """Complaint model with ward selection and priority"""
    
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
    
    PRIORITY_CHOICES = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent'),
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
    image = models.ImageField(upload_to=complaint_image_path, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='Normal',
        help_text="Priority level - Auto-flagged as Urgent after 7 days"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Override save to compress image and update priority before saving"""
        # Auto-update priority if older than 7 days and not resolved
        if self.pk and self.status != 'Resolved':
            days_old = (timezone.now() - self.created_at).days
            if days_old >= 7:
                self.priority = 'Urgent'
        
        if self.image:
            # Open the image
            img = Image.open(self.image)
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if image is too large (max 1920x1080)
            max_size = (1920, 1080)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Compress and save to BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # Replace the image file with compressed version
            self.image = InMemoryUploadedFile(
                output,
                'ImageField',
                f"{self.image.name.split('.')[0]}.jpg",
                'image/jpeg',
                output.getbuffer().nbytes,
                None
            )
        
        super().save(*args, **kwargs)
    
    def update_priority(self):
        """Auto-update priority to Urgent if complaint is older than 7 days and not resolved"""
        if self.status != 'Resolved':
            days_old = (timezone.now() - self.created_at).days
            if days_old >= 7 and self.priority != 'Urgent':
                self.priority = 'Urgent'
                self.save(update_fields=['priority'])
                return True
        return False
    
    def is_old(self):
        """Check if complaint is older than 7 days"""
        return (timezone.now() - self.created_at).days >= 7
    
    def days_since_creation(self):
        """Get number of days since complaint was created"""
        return (timezone.now() - self.created_at).days
    
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
            models.Index(fields=['priority', 'status']),
        ]


class Remark(models.Model):
    """Admin internal remarks/notes for complaints"""
    
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='remarks'
    )
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_remarks'
    )
    remark = models.TextField(help_text="Internal note visible only to admins")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Remark by {self.admin_user.fullname} on Complaint #{self.complaint.id}"
    
    class Meta:
        db_table = 'complaint_remarks'
        ordering = ['-created_at']
        verbose_name = 'Admin Remark'
        verbose_name_plural = 'Admin Remarks'