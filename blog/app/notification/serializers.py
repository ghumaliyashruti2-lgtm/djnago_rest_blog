from rest_framework import serializers
from app.notification.models import Notification
from rest_framework.exceptions import PermissionDenied



class NotificationSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ["user_id", "message", "is_read", "created_at"]

    def get_message(self, obj):
        sender_name = obj.sender.username if obj.sender else "Someone"

        if obj.type == "comment":
            return f"{sender_name} commented on your post"

        elif obj.type == "reply":
            comment_text = obj.comment.text if obj.comment else ""
            return f'{sender_name} replied to your comment "{comment_text}"'

        elif obj.type == "like": 
            return f"{sender_name} liked your post"
        
        elif obj.type == "follow":
            return f"{sender_name} started following you"

        return "New notification"
    

class MarkNotificationReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = []  # no input needed

    def update(self, instance, validated_data):
        request = self.context["request"]

        if instance.user != request.user:
            raise PermissionDenied("You cannot modify this notification")

        instance.is_read = True
        instance.save()
        return instance
    
class DeleteNotificationSerializer(serializers.Serializer):

    def delete(self, instance):
        request = self.context["request"]

        if instance.user != request.user:
            raise PermissionDenied("You cannot delete this notification")

        instance.delete()
        return instance