from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
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