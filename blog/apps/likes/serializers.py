# app/like/serializers.py

from rest_framework import serializers
from django.shortcuts import get_object_or_404
from apps.likes.models import Like
from apps.posts.models import Post
from apps.notifications.views import create_notification
from apps.follows.models import Follow
import logging
logger =logging.getLogger(__name__)

class ToggleLikeSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()

    def validate_post_id(self, value):
        logger.debug(f"user Fetching like or unlike toggle on post id={value}  ")
        try:
            return Post.objects.get(id=value)
        except Post.DoesNotExist:
            logger.error(f"Post not found: id={value}")
            raise serializers.ValidationError("Post not found")

    def save(self, **kwargs):
        request = self.context["request"]
        user = request.user
        post = self.validated_data["post_id"]
        if post.user == user:
            logger.debug(f"User {user.username} toggling like on own post {post.id}")
        else:
            logger.debug(f"User {user.username} toggling like on post {post.id}")

        # PRIVATE ACCOUNT CHECK
        if post.user != user:
            if post.is_private:
                is_following = Follow.objects.filter(
                    follower=user,
                    following=post.user
                ).exists()

                if not is_following:
                    logger.error(f"Unauthorized User {request.user.username} tried to like on private post {post.id}")
                    raise serializers.ValidationError("Account is private")

        like = Like.objects.filter(user=user, post=post).first()

        # UNLIKE
        if like:
            like.delete()
            if post.user == user :
                logger.warning(f"User {user.username} unlike own post: {post.id}")
            else:
                logger.warning(f"User {user.username} unlike post: {post.id}")
            return {
                "post_id":post.id,
                "message": "Post unliked",
                "likes_count": post.likes.count()
            }

        # LIKE
        Like.objects.create(user=user, post=post)
        if post.user == user :
            logger.warning(f"User {user.username} like own post: {post.id}")
        else:
            logger.info(f"User {user.username} like post: {post.id}")
        # Notification (only once, correct type)
        if post.user != user:
            create_notification(
                user=post.user,
                sender=user,
                type="like",
                post=post
            )
        logger.info(f"like notification sent to user : {post.user.username}")

        return {
            "post_id":post.id,
            "message": "Post liked",
            "likes_count": post.likes.count()
        }