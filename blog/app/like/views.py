from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from app.like.models import Like
from app.post.models import Post
from app.notification.views import create_notification
from app.like.serializers import ToggleLikeSerializer


class ToggleLikeView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        
        serializer = ToggleLikeSerializer(
            data = {"post_id":post_id},
            context={"request":request}
        )
        
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        
        return Response(data)
