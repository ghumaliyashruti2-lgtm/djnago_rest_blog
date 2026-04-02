from django.db import models

# Create your models here.
from django.conf import settings
from app.post.models import Post
from app.comment.models import Comment

class Notification(models.Model):

    user = models.ForeignKey(   # receiver
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_notifications"
    )

    sender = models.ForeignKey(  # who did action
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )
    
    message = models.TextField(blank=True)

    type = models.CharField(max_length=50)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.type} - {self.user}"