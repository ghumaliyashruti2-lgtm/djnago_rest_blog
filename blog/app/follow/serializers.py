from rest_framework import serializers
from app.follow.models import Follow


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
        read_only_fields = ["id", "follower", "created_at"]

    def validate(self, data):
        request = self.context.get("request")
        follower = request.user
        following = data.get("following")

        if follower == following:
            raise serializers.ValidationError("You cannot follow yourself")

        if Follow.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError("Already following this user")

        return data

    def create(self, validated_data):
        validated_data["follower"] = self.context["request"].user
        return super().create(validated_data)