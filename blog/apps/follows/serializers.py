from rest_framework import serializers
from apps.follows.models import Follow
from django.shortcuts import get_object_or_404
from apps.users.models import User
from apps.notifications.views import NotificationType, create_notification
from rest_framework.permissions import IsAuthenticated
import logging
logger = logging.getLogger(__name__)

class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source="follower.username", read_only=True)
    following_username = serializers.CharField(source="following.username", read_only=True)

    class Meta:
        model = Follow
        fields = [
            "id",
            "follower",
            "follower_username",
            "following",
            "following_username",
            "created_at"
        ]
        
        read_only_fields = ["id", "follower", "created_at" , "following"]
        

    def validate(self, data):
        request = self.context.get("request")
        follower = request.user
        following = self.context.get("following")
        
        logger.debug(f"Validate follow: follower={follower}, following={getattr(following, 'username', None)}")

        if not following:
            logger.error(f"user not found {following}")
            raise serializers.ValidationError({"following": "Invalid user"})  

        if follower == following:
            logger.error(f"User {follower} tried to follow themselves")
            raise serializers.ValidationError("You cannot follow yourself")

        return data
    
    def save(self, **kwargs):
        request = self.context.get("request")
        follower = request.user
        following = self.context.get("following") 

        follow = Follow.objects.filter(
            follower=follower,
            following=following
        ).first()


        # ======================
        # UNFOLLOW
        # ======================
        if follow:
            logger.debug(f"user {follower} try to unfollow user {following}")
            follow.delete()
            logger.info(f"User {follower} successfully unfollowed user {following}")
            return {"message": "Unfollowed"}

        # ======================
        # FOLLOW
        # ======================
        if follow is None:
            logger.debug(f"user {follower} try to follow user {following}")
            follow = Follow.objects.create(
                follower=follower,
                following=following
            )
        
        logger.info(f"User {follower} successfully start to followed user {following}")

        #  Notification (optional)
        if following != follower:
            create_notification(
                user=following,
                sender=follower,
                type=NotificationType.FOLLOW
            )
        logger.debug(f"Follow notification sent to user {following}")
        return {
            "message": "Followed",
            "data":{
                "follower":follower.username,
                "following":following.username}
        }
        
        
class FollowStatusSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()
    is_following = serializers.BooleanField(read_only=True)
    message =serializers.CharField(read_only=True)
    
    def to_representation(self, instance):
    
        request = self.context.get("request")
        follower = request.user
        following = instance
        
        logger.debug(f"user {request.user} Check follow status for user={instance.username} ")
        
        is_following = Follow.objects.filter(
            follower=follower,
            following=following
        ).exists()
        
        message = (
            f"{follower} You are following {following.username}"
            if is_following
            else f"{follower} You are not following {following.username}"
        )
        
        logger.info(f"{message}")
        
        return {
            "following_user_id": following.id,
            "is_following": is_following,
            "message": message
        }
    
        
class MyFollowerSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source="follower.username", read_only=True)

    class Meta:
        model = Follow
        fields = [
            "id",
            "follower",
            "follower_username",
            "created_at"
        ]
        
class MyFollowingSerializer(serializers.ModelSerializer):
    following_username = serializers.CharField(source="following.username", read_only=True)

    class Meta:
        model = Follow
        fields = [
            "id",
            "following",
            "following_username",
            "created_at"
        ]