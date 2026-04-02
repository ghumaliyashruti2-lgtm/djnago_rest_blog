from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from app.like.models import Like
from app.post.models import Post
from app.notification.views import create_notification


class ToggleLikeView(GenericAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):

        post = get_object_or_404(Post, id=post_id)
        user = request.user

        like = Like.objects.filter(user=user, post=post).first()

        # 🔴 UNLIKE
        if like:
            like.delete()
            likes_count = post.likes.count()

            return Response({
                "message": "Post unliked",
                "likes_count": likes_count
            }, status=200)

        # 🟢 LIKE
        Like.objects.create(user=user, post=post)

        # 🔔 Notification
        if post.user != user:
            create_notification(
                user=post.user,
                sender=user,
                type="like",
                post=post
            )

        likes_count = post.likes.count()

        return Response({
            "message": "Post liked",
            "likes_count": likes_count
        }, status=200)
        
        