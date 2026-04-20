from rest_framework import serializers
from apps.follows.models import Follow
from django.shortcuts import get_object_or_404
from apps.users.models import User
from apps.notifications.views import NotificationType, create_notification
from rest_framework.permissions import IsAuthenticated

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

        if not following:
            raise serializers.ValidationError({"following": "Invalid user"})  

        if follower == following:
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
            follow.delete()
            return {"message": "Unfollowed"}

        # ======================
        # FOLLOW
        # ======================
        follow = Follow.objects.create(
            follower=follower,
            following=following
        )

        #  Notification (optional)
        if following != follower:
            create_notification(
                user=following,
                sender=follower,
                type=NotificationType.FOLLOW
            )

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

    def validate_user_id(self, value):
        user = get_object_or_404(User, id=value)
        request = self.context["request"]
        
        if request.user == user:
            raise serializers.ValidationError("You cannot follow yourself")
        
        return user
    
    def to_representation(self, instance):
    
        request = self.context.get("request")
        follower = request.user
        following = instance
         
        is_following = Follow.objects.filter(
            follower=follower,
            following=following
        ).exists()
        
        message = (
            f"You followed  {following.username}"
            if is_following
            else f"You not followed  {following.username}"
        )
        
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