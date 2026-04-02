from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from app.post.models import Post   

class Comment(models.Model):

    text = models.TextField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_comments"
    )

    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_comments",
        null=True,
        blank=True
    )

    

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text