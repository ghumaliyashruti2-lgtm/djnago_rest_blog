from rest_framework import serializers
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
import logging

from apps.posts.models import Post
from apps.comments.models import Comment
from apps.follows.models import Follow
from apps.users.models import User
from apps.likes.models import Like

logger = logging.getLogger(__name__)


# ======================
# POST SERIALIZER
# ======================

class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "title", "content", "image","summary",
            "user", "is_private", "created_at",
            "average_rating", "total_ratings"
        ]
        read_only_fields = [
            "id", "user", "created_at","summary",
            "average_rating", "total_ratings"
        ]
        depth = 1

    # ======================
    # VALIDATIONS
    # ======================

    def validate_title(self, value):
        value = value.strip()

        if not value:
            logger.error("Empty title provided")
            raise serializers.ValidationError("Title cannot be empty")

        if len(value) < 3:
            logger.error(f"Short title provided: '{value}'")
            raise serializers.ValidationError("Title too short")

        return value

    def validate_content(self, value):
        value = value.strip()

        if not value:
            logger.error("Empty content provided")
            raise serializers.ValidationError("Content cannot be empty")

        return value

    def validate_image(self, value):
        if value.size > 2 * 1024 * 1024:
            logger.error(f"Large image upload attempted: size={value.size}")
            raise serializers.ValidationError("Image size should be less than 2MB")
        return value

    # ======================
    # CREATE
    # ======================

    def create(self, validated_data):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            logger.error("Request context missing or unauthenticated user")
            raise serializers.ValidationError("Authentication required")

        validated_data["user"] = request.user
        post = super().create(validated_data)

        logger.info(f"Post created: post_id={post.id}, user={request.user.username}")
        return post

    # ======================
    # RATING
    # ======================

    def get_average_rating(self, obj):
        return obj.ratings.aggregate(avg=Avg('rating'))['avg']

    def get_total_ratings(self, obj):
        return obj.ratings.count()

    # ======================
    # FILTER POSTS (CORE LOGIC)
    # ======================

    @staticmethod
    def get_filtered_posts(request):
        user = request.user
        user_id = request.query_params.get("user_id")
        username = request.query_params.get("username")

        logger.debug(
            f"Fetching posts by user: {user.username if user.is_authenticated else 'anonymous'}"
        )

        # ======================
        # PROFILE POSTS
        # ======================
        if user_id or username:
            target_user = get_object_or_404(
                User,
                id=user_id if user_id else None,
                username=username if username else None
            )

            is_following = False
            if user.is_authenticated:
                is_following = Follow.objects.filter(
                    follower=user,
                    following=target_user
                ).exists()

            # PRIVATE ACCOUNT CHECK
            if target_user.is_private and not (user == target_user or is_following):
                logger.warning(
                    f"Unauthorized access: user={user if user.is_authenticated else 'anonymous'} "
                    f"tried to access private user={target_user.id}"
                )
                raise PermissionDenied("Account is private")

            # POST VISIBILITY
            if user == target_user or is_following:
                posts = Post.objects.filter(user=target_user)
            else:
                posts = Post.objects.filter(
                    user=target_user,
                    is_private=False
                )

        # ======================
        # FEED
        # ======================
        else:
            if user.is_authenticated:
                following_ids = Follow.objects.filter(
                    follower=user
                ).values_list("following_id", flat=True)

                posts = Post.objects.filter(
                    Q(is_private=False) |
                    Q(user=user) |
                    Q(user__id__in=following_ids)
                ).distinct()
            else:
                posts = Post.objects.filter(is_private=False)

        posts = posts.order_by("-created_at")

        logger.info(
            f"Posts fetched successfully by user: {user.username if user.is_authenticated else 'anonymous'}"
        )
        return posts

    # ======================
    # USER POSTS
    # ======================

    @staticmethod
    def get_user_posts(user):
        logger.info(f"User {user.username} fetching own posts")
        return Post.objects.filter(user=user).order_by("-created_at")

    # ======================
    # USER STATS
    # ======================

    @staticmethod
    def get_user_stats(user):
    
        return {
            "id": user.id,
            "username": user.username,
            "is_private": user.is_private,
            "posts": Post.objects.filter(user=user).count(),
            "comments": Comment.objects.filter(user=user).count(),
            "likes": Like.objects.filter(user=user).count(),
            "followers": Follow.objects.filter(following=user).count(),
            "followings": Follow.objects.filter(follower=user).count(),
        }


# ======================
# DELETE SERIALIZER
# ======================

class DeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate_id(self, value):
        logger.debug(f"Delete request for post id={value}")
        return value

    def delete(self, instance):
        logger.warning(f"Post deleted: id={instance.id}, user={instance.user.username}")
        instance.delete()
        return {"message": "Post deleted successfully"}