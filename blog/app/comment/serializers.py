from rest_framework import serializers
from app.comment.models import Comment
from app.post.serializers import PostSerializer
from app.user.serializers import ProfileSerializer
from app.notification.views import create_notification
from rest_framework.exceptions import PermissionDenied

from app.follow.models import Follow

# ======================
# COMMENT SERIALIZER
# ======================
  
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    post = PostSerializer(read_only=True)
    user = ProfileSerializer(read_only=True)

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

   
            
    def create(self, validated_data):
        request = self.context["request"]
        post = self.context["post"]

        # check account private or not 
        if post.user != request.user:  
            
            if post.user.is_private:  
                
                is_following = Follow.objects.filter(
                    follower=request.user,
                    following=post.user
                ).exists()

                if not is_following:
                    raise serializers.ValidationError("Account is private")

        # Create comment
        comment = Comment.objects.create(
            text=validated_data["text"],
            user=request.user,
            post=post
        )

        # Notification
        if post.user != request.user:
            create_notification(
                user=post.user,
                sender=request.user,
                type="comment",
                post=post,
                comment=comment
            )

        return comment


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
        try:
            parent = Comment.objects.get(id=value)
        except Comment.DoesNotExist:
            raise serializers.ValidationError("Parent comment not found")

        if parent.parent is not None:
            raise serializers.ValidationError("Nested replies not allowed")

        return value

    def create(self, validated_data):
        request = self.context["request"]
        parent = Comment.objects.get(id=validated_data["parent_id"])
        post = parent.post

        if post.user != request.user:
            if post.user.is_private:
                is_following = Follow.objects.filter(
                    follower=request.user,
                    following=post.user
                ).exists()

                if not is_following:
                    raise serializers.ValidationError("Account is private")
                
        comment = Comment.objects.create(
            text=validated_data["text"],
            user=request.user,
            post=parent.post,
            parent=parent
        )

        # Notification logic
        if parent.user != request.user:
            create_notification(
                user=parent.user,
                sender=request.user,
                type="reply",
                post=parent.post,
                comment=comment
            )

        return comment
    
    
# ========================
# UPDATE COMMENT
# ========================
class UpdateCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["text"]

    def update(self, instance, validated_data):
        request = self.context["request"]

        if instance.user != request.user:
            raise PermissionDenied("You cannot edit this comment")

        instance.text = validated_data["text"]
        instance.save()
        return instance
    
# ===============================
# DELETE COMMENT
# ===============================

class DeleteCommentSerializer(serializers.Serializer):

    def delete(self, instance):
        request = self.context["request"]

        if instance.user != request.user:
            raise PermissionDenied("You cannot delete this comment")

        instance.delete()
        return instance