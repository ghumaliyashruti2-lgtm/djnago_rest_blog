from rest_framework import serializers
from apps.comments.models import Comment
from apps.posts.models import Post
from apps.posts.serializers import PostSerializer
from apps.users.serializers import ProfileSerializer
from apps.notifications.views import create_notification
import logging
logger = logging.getLogger(__name__)
from apps.follows.models import Follow


# ======================
# COMMENT SERIALIZER
# ======================
  
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "text", "user", "post", "parent", "replies"]
        read_only_fields = ["id", "user", "post", "replies"]

    def get_replies(self, obj):
        request = self.context["request"]
        children = obj.replies.all()
        logger.debug(f"Fetching replies from user {request.user.username} for comment id={obj.id}, count={children.count()}")
        return CommentSerializer(children, many=True, context=self.context).data
    
# ======================
# CREATE COMMENT
# ======================

class CreateCommentSerializer(serializers.Serializer):
    
    text = serializers.CharField(max_length=500)
    
    def validate_text(self, value):
        request = self.context["request"]
        value = value.strip()

        if not value:
            logger.error(f"Empty comment attempt by user {request.user.username}")
            raise serializers.ValidationError("Comment cannot be empty")

        if len(value) < 2:
            logger.error(f"user {request.user.username} enter too short Comment ")
            raise serializers.ValidationError("Comment too short")

        return value

   
            
    def create(self, validated_data):
        request = self.context["request"]
        post = validated_data["post"]
        
        logger.debug(f"User {request.user.username} trying to comment on post {post.id}")

        # check account private or not 
        if post.user != request.user:  
            
            if post.user.is_private:  
                
                is_following = Follow.objects.filter(
                    follower=request.user,
                    following=post.user
                ).exists()

                if not is_following:
                    logger.error(f"User {request.user.username} tried to comment on private post {post.id}")
                    raise serializers.ValidationError("Account is private")

        # Create comment
        comment = Comment.objects.create(
            text=validated_data["text"],
            user=request.user,
            post=post
        )
        logger.info(f"Comment created: user={request.user.username}, post={post.id}, comment_id={comment.id}")


        # Notification
        if post.user != request.user:
            create_notification(
                user=post.user,
                sender=request.user,
                type="comment",
                post=post,
                comment=comment
            )
            logger.debug(f"Notification sent user {request.user.username} for comment {comment.id}")
        return comment


# ======================
# REPLY COMMENT
# ======================
class ReplyCommentSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=500)
    parent_id = serializers.IntegerField()

    def validate_text(self, value):
        request = self.context["request"]
        value = value.strip()

        if not value:
            logger.error(f"user {request.user.username} Empty reply attempt")
            raise serializers.ValidationError("Reply cannot be empty")

        return value

    def validate_parent_id(self, value):
        request = self.context["request"]
        try:
            parent = Comment.objects.get(id=value)
        except Comment.DoesNotExist:
            logger.error(f"user {request.user.username} attempt parent comment id={value} is not found ")
            raise serializers.ValidationError("Parent comment not found")

        if parent.parent is not None:
            logger.error(f"{request.user.username} attempt Nested reply on comment {value} is not allowed")
            raise serializers.ValidationError("Nested replies not allowed")

        return value

    def create(self, validated_data):
        request = self.context["request"]
        parent = Comment.objects.get(id=validated_data["parent_id"])
        post = parent.post
        
        logger.debug(f"User {request.user.username} replying to comment {parent.id} on post {post.id}")

        if post.user != request.user:
            if post.user.is_private:
                is_following = Follow.objects.filter(
                    follower=request.user,
                    following=post.user
                ).exists()

                if not is_following:
                    logger.error(f"Unauthorized reply attempt: user={request.user.username}, post={post.id}")
                    raise serializers.ValidationError("Account is private")
                
        comment = Comment.objects.create(
            text=validated_data["text"],
            user=request.user,
            post=parent.post,
            parent=parent
        )
        logger.info(
            f"Reply created: user={request.user.username}, parent={parent.id}, comment_id={comment.id}"
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
            logger.debug(f"Notification sent to user {request.user.username} for reply comment id {comment.id}")

        return comment
    
    
# ========================
# UPDATE COMMENT
# ========================
class UpdateCommentSerializer(serializers.Serializer):
    text = serializers.CharField()

    def update(self, instance, validated_data):
        request = self.context["request"]
        logger.debug(f"user {request.user.username} try to update comment {instance.id}")
        old_text = instance.text
        instance.text = validated_data.get("text",instance.text)
        instance.save()
        logger.info(
            f"user {request.user.username} updated Comment: id={instance.id}, old='{old_text}', new='{instance.text}'"
        )
        return instance
    