from django.db import models

# Create your models here.
from django.db import models

class AadhaarVerification(models.Model):
    refid = models.CharField(max_length=20, unique=True)
    aadhaar_number = models.CharField(max_length=12)
    verification_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Aadhaar: {self.aadhaar_number} - Verified: {self.verification_status}"
    
class PanCardVerification(models.Model):
    refid = models.CharField(max_length=20, unique=True)
    pan_number = models.CharField(max_length=10, unique=True)
    verification_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PAN: {self.pan_number} - Verified: {self.verification_status}"
