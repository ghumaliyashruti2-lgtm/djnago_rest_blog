from rest_framework import serializers
from django.db.models import Avg
from app.post.models import Post
from app.comment.models import Comment
from app.follow.models import Follow 
from app.user.models import User
from app.like.models import Like
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q


# ======================
# POST SERIALIZER
# ======================

class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "title", "content", "image", "user", "is_private", "created_at","average_rating", "total_ratings"]
        read_only_fields = ["id", "user", "created_at","average_rating", "total_ratings"]

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Title cannot be empty")

        if len(value) < 3:
            raise serializers.ValidationError("Title too short")

        return value

    def validate_content(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Content cannot be empty")

        return value

    def validate_image(self, value):
        if value.size > 2 * 1024 * 1024:  # 2MB
            raise serializers.ValidationError("Image size should be less than 2MB")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)
    
    def get_average_rating(self, obj):
        return obj.ratings.aggregate(avg=Avg('rating'))['avg']

    def get_total_ratings(self, obj):
        return obj.ratings.count()

    
    @staticmethod
    def get_filtered_posts(request):
        user = request.user
        user_id = request.query_params.get("user_id")
        username = request.query_params.get("username")

        # PROFILE POSTS
        if user_id or username:
            if user_id:
                target_user = get_object_or_404(User, id=user_id)
            else:
                target_user = get_object_or_404(User, username=username)

            # PRIVATE ACCOUNT CHECK
            if target_user.is_private:
                if not user.is_authenticated:
                    raise PermissionDenied("Account is private")

                is_following = Follow.objects.filter(
                    follower=user,
                    following=target_user
                ).exists()

                if not is_following and user != target_user:
                    raise PermissionDenied("Account is private")

            # POST FILTER
            if user.is_authenticated:
                posts = Post.objects.filter(user=target_user).filter(
                    Q(is_private=False) |
                    Q(user=user) |
                    Q(user__followers__follower=user)
                ).distinct()
            else:
                posts = Post.objects.filter(
                    user=target_user,
                    is_private=False
                )

        # FEED
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

        return posts.order_by("-created_at")

    # =========================
    # USER POSTS
    # =========================
    @staticmethod
    def get_user_posts(user):
        return Post.objects.filter(user=user).order_by("-created_at")

    # =========================
    # USER STATS
    # =========================
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

    @staticmethod
    def get_user_stats_by_username(username):
        user = get_object_or_404(User, username=username)
        return PostSerializer.get_user_stats(user)

    # =========================
    # PERMISSION CHECK
    # =========================
    @staticmethod
    def validate_post_owner(request_user, post):
        if post.user != request_user:
            raise PermissionDenied("Not allowed")