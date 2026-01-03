from django.db import models
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
import uuid

User = get_user_model()


class ComplainsCategory(models.Model):
    name_en = models.CharField(max_length=100)
    name_np = models.CharField(max_length=100)
    icon_name = models.CharField(max_length=50, blank=True, help_text="Icon identifier (e.g., 'road', 'water', 'electricity')")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name_np']
        verbose_name_plural = "Complaint Categories"

    def __str__(self):
        return f"{self.name_np} ({self.name_en})"



class Complaint(models.Model):
    STATUS = (
        ('PENDING', 'प्रक्रियामा'),
        ('IN_PROGRESS', 'जाँच भइरहेको'),
        ('RESOLVED', 'समाधान भयो'),
        ('REJECTED', 'अस्वीकृत'),
    )

    # Unique ID for tracking (shown to citizens)
    complaint_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # User info
    citizen = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='complaints')
    citizen_phone = models.CharField(max_length=15, blank=True, help_text="For anonymous submissions")
    
    # Complaint details
    category = models.ForeignKey(ComplainsCategory, on_delete=models.PROTECT, related_name='complaints')
    title = models.CharField(max_length=255, blank=True, help_text="Short title")
    description = RichTextField(blank=True, null=True, config_name='default')
    
    # Media
    image = models.ImageField(upload_to='complaints/%Y/%m/%d', blank=True, null=True)
    voice_note = models.FileField(upload_to='voice/%Y/%m/%d', blank=True, null=True)
    
    # Location
    location_text = models.CharField(max_length=255, blank=True, help_text="Ward, area description")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=STATUS, default='PENDING')
    admin_notes = models.TextField(blank=True, help_text="Internal notes for officials")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    synced_at = models.DateTimeField(null=True, blank=True, help_text="When offline data was synced")
    
    # Offline support
    client_created_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp from offline device")
    is_offline_submission = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['complaint_id']),
        ]

    def __str__(self):
        return f"#{str(self.complaint_id)[:8]} - {self.category.name_np} - {self.get_status_display()}"
    
    def get_sms_message(self):
        """Generate SMS-like notification message"""
        return f"तपाईंको उजुरी नं. {str(self.complaint_id)[:8]} प्राप्त भयो। अवस्था: {self.get_status_display()}"