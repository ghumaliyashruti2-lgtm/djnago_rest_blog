# app/like/serializers.py

from rest_framework import serializers
from django.shortcuts import get_object_or_404
from app.like.models import Like
from app.post.models import Post
from app.notification.views import create_notification
from app.follow.models import Follow

class ToggleLikeSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()

    def validate_post_id(self, value):
        return get_object_or_404(Post, id=value)

    def save(self, **kwargs):
        request = self.context["request"]
        user = request.user
        post = self.validated_data["post_id"]

        # PRIVATE ACCOUNT CHECK
        if post.user != user:
            if post.user.is_private:
                is_following = Follow.objects.filter(
                    follower=user,
                    following=post.user
                ).exists()

                if not is_following:
                    raise serializers.ValidationError("Account is private")

        like = Like.objects.filter(user=user, post=post).first()

        # UNLIKE
        if like:
            like.delete()
            return {
                "message": "Post unliked",
                "likes_count": post.likes.count()
            }

        # LIKE
        Like.objects.create(user=user, post=post)

        # Notification (only once, correct type)
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