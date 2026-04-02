from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from app.post.models import Post   # adjust path

User = get_user_model()

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="ratings")
    rating = models.IntegerField()  

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']  