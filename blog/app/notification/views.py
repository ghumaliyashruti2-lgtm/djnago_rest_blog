from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from app.notification.models import Notification
from app.notification.serializers import NotificationSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.mixins import DestroyModelMixin

# ======================
# CREATE NOTIFICATION (helper)
# ======================
def create_notification(user, sender, type, post=None, comment=None):

    # duplicate notification handle 
    exists = Notification.objects.filter(
        user=user,
        sender=sender,
        type=type,   
        post=post,
        comment=comment
    ).exists()

    if exists:
        return

    if type == NotificationType.LIKE:
        message = f"{sender.username} liked your post"
    elif type == NotificationType.COMMENT:
        message = f"{sender.username} commented on your post"
    elif type == NotificationType.REPLY:
        message = f"{sender.username} replied to your comment"
    elif type == NotificationType.FOLLOW:
        message = f"{sender.username} started following you"
    else:
        message = ""

    Notification.objects.create(
        user=user,
        sender=sender,
        type=type,
        post=post,
        comment=comment,
        message=message  
    )
class NotificationType:
    LIKE = "like"
    COMMENT = "comment"
    REPLY = "reply"
    FOLLOW = "follow"


# ======================
# GET NOTIFICATIONS
# ======================
class NotificationListView(ListAPIView):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'is_read', 'sender']
    
    search_fields = ['message']

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")
        
# ======================
# MARK AS READ
# ======================

class NotificationMarkReadView(UpdateModelMixin, GenericAPIView):

    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()

    def put(self, request, *args, **kwargs):

        notification = self.get_object()

        if notification.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        notification.is_read = True
        notification.save()

        return Response({"message": "Marked as read"})

# ======================
# DELETE NOTIFICATION
# ======================

class NotificationDeleteView(DestroyModelMixin, GenericAPIView):

    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()

    def delete(self, request, *args, **kwargs):

        notification = self.get_object()

        if notification.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        notification.delete()

        return Response({"message": "Notification deleted"})
    
        
# ======================
# MARK AS UN-READ
# ======================

class UnreadCountView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            is_read=False
        )

    def get(self, request, *args, **kwargs):
        return Response({"unread": self.get_queryset().count()})