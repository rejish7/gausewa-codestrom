from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string


class OTP(models.Model):
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.phone_number} - {self.otp_code}"
    
    def is_valid(self):
        """Check if OTP is still valid and not expired"""
        return not self.is_verified and self.expires_at > timezone.now() and self.attempts < 3
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    @classmethod
    def create_otp(cls, phone_number, expiry_minutes=5):
        """Create a new OTP for a phone number"""
        otp_code = cls.generate_otp()
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        # Invalidate any previous OTPs for this phone number
        cls.objects.filter(phone_number=phone_number, is_verified=False).update(is_verified=True)
        
        otp = cls.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at
        )
        return otp
    
    def verify(self, submitted_otp):
        """Verify the submitted OTP"""
        self.attempts += 1
        self.save()
        
        if not self.is_valid():
            return False
        
        if self.otp_code == submitted_otp:
            self.is_verified = True
            self.save()
            return True
        
        return False
