# app/like/serializers.py

from rest_framework import serializers
from django.shortcuts import get_object_or_404

from app.like.models import Like
from app.post.models import Post
from app.notification.views import create_notification


class ToggleLikeSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()

    def validate_post_id(self, value):
        return get_object_or_404(Post, id=value)  

    def save(self, **kwargs):
        user = self.context["request"].user
        post = self.validated_data["post_id"]

        like = Like.objects.filter(user=user, post=post).first()

        # UNLIKE
        if like:
            like.delete()
            return {
                "message": "Post unliked",
                "likes_count": post.likes.count()
            }

        #  LIKE
        Like.objects.create(user=user, post=post)

        if post.user != user:
            create_notification(
                user=post.user,
                sender=user,
                type="like",
                post=post
            )

        return {
            "message": "Post liked",
            "likes_count": post.likes.count()
        }
    