from django.db import models

# Create your models here.
from django.conf import settings


class Post(models.Model):

    title = models.CharField(max_length=200)
    content = models.TextField()
    
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)

    is_private = models.BooleanField(default=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title