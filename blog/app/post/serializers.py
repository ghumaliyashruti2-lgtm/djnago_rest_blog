from rest_framework import serializers
from django.db.models import Avg
from app.post.models import Post
from app.comment.models import Comment


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

# ======================
# COMMENT SERIALIZER
# ======================
class PostCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["id", "text", "post", "user"]


# ======================
# SEARCH SERIALIZER
# ======================
class SearchSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=100)

    def validate_query(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Search query required")

        if len(value) < 2:
            raise serializers.ValidationError("Search query too short")

        return value
    
    