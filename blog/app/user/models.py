from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    profile_pic = models.ImageField(
        upload_to="profile_pics/",
        default="profile_pictures/default_profile.png"
    )
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] 
    
    

class OTP(models.Model):
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=2)
