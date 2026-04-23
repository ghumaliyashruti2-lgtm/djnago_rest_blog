from rest_framework import serializers
from apps.notifications.models import Notification
import logging
logger = logging.getLogger(__name__)


class NotificationSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ["id","user_id", "message", "is_read", "created_at"]

    def get_message(self, obj):
        logger.debug(f"Generating notification message by user {obj.user} notification id={obj.id}, type={obj.type}")
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
        
        elif obj.type == "rating":
            return f"{sender_name} rate on your post"
        
        logger.warning(f"Unknown notification type: {obj.type}")
        return "New notification"
    

class MarkNotificationReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = [] 

    def update(self, instance, validated_data):
        logger.debug(f"fetching notificaton {instance.id} for mark as read")
        instance.is_read = True
        instance.save()
        logger.info(f"Notification marked as read id={instance.id} by user {instance.user}")
        return instance
    
class DeleteNotificationSerializer(serializers.Serializer):

    def delete(self, instance):
        id = instance.id
        instance.delete()
        logger.info(f"user {instance.user} deleted Notification id {id}")
        return instance
    

# ====================
# READ COUNT 
# =====================

class UnreadCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()