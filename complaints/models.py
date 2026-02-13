from django.db import models
from django.conf import settings
import uuid
import os
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def complaint_image_path(instance, filename):
    """Generate unique filename using UUID"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('complaints', filename)

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
    image = models.ImageField(upload_to=complaint_image_path, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Override save to compress image before saving"""
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