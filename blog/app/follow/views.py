# app/follow/views.py

from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin

from app.follow.models import Follow
from app.follow.serializers import FollowSerializer
from app.notification.views import create_notification
from app.notification.views import NotificationType
User = get_user_model()


class ToggleFollowView(CreateModelMixin, DestroyModelMixin, GenericAPIView):

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    queryset = Follow.objects.all()

    def post(self, request, user_id):

        target_user = get_object_or_404(User, id=user_id)
        current_user = request.user

        # ❌ Cannot follow yourself
        if current_user == target_user:
            return Response({"error": "You cannot follow yourself"}, status=400)

        follow = Follow.objects.filter(
            follower=current_user,
            following=target_user
        ).first()

        # ======================
        # 🔴 UNFOLLOW
        # ======================
        if follow:
            follow.delete()
            return Response({"message": "Unfollowed"}, status=200)

        # ======================
        # 🟢 FOLLOW
        # ======================
        serializer = self.get_serializer(data={
            "following": target_user.id
        })

        serializer.is_valid(raise_exception=True)
        serializer.save(follower=current_user)

        # 🔔 Notification (optional)
        if target_user != current_user:
            create_notification(
                user=target_user,
                sender=current_user,
                type=NotificationType.FOLLOW
            )

        return Response({
            "message": "Followed",
            "data": serializer.data
        }, status=201)
        
        
class FollowStatusView(GenericAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):

        is_following = Follow.objects.filter(
            follower=request.user,
            following_id=user_id
        ).exists()
        
        if is_following == True:
            return Response({
                "You followed user_id ": user_id,
                "is_following": is_following
            })
            
        else:
            return Response({
                "You Not followed user_id ": user_id,
                "is_following": is_following
            })
            
        
class MyFollowersView(ListAPIView):

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['follower', 'following']

    def get_queryset(self):
        return Follow.objects.filter(
            following=self.request.user
        ).select_related("follower", "following")

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            return Response({
                "message": "No one follows you",
                "data": []
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
class MyFollowingView(ListAPIView):

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['follower', 'following']

    def get_queryset(self):
        return Follow.objects.filter(
            follower=self.request.user
        ).select_related("follower", "following")

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            return Response({
                "message": "You are not following anyone",
                "data": []
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        