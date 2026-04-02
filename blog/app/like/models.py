from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from app.post.models import Post   


class Like(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_likes"
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )
     
class Meta:
    unique_together = ['user', 'post']