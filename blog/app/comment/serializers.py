from rest_framework import serializers
from app.comment.models import Comment


# ======================
# COMMENT SERIALIZER
# ======================
  
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "text", "user", "post", "parent", "replies"]
        read_only_fields = ["id", "user", "post", "replies"]

    def get_replies(self, obj):
        children = obj.replies.all()
        return CommentSerializer(children, many=True, context=self.context).data



# ======================
# CREATE COMMENT
# ======================
class CreateCommentSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=500)

    def validate_text(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Comment cannot be empty")

        if len(value) < 2:
            raise serializers.ValidationError("Comment too short")

        return value


# ======================
# REPLY COMMENT
# ======================
class ReplyCommentSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=500)
    parent_id = serializers.IntegerField()

    def validate_text(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Reply cannot be empty")

        return value

    def validate_parent_id(self, value):
        if not Comment.objects.filter(id=value).exists():
            raise serializers.ValidationError("Parent comment not found")
        return value

    def validate(self, data):
        parent = Comment.objects.get(id=data["parent_id"])

        # Optional: only allow 1-level replies
        if parent.parent is not None:
            raise serializers.ValidationError("Nested replies not allowed")

        return data    
  