# app/follow/views.py

from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from app.follow.models import Follow
from app.follow.serializers import FollowSerializer, FollowStatusSerializer, MyFollowerSerializer, MyFollowingSerializer

User = get_user_model()


class ToggleFollowView(CreateModelMixin, DestroyModelMixin, GenericAPIView):

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    queryset = Follow.objects.all()

    def post(self, request, user_id):
       following = get_object_or_404(User, id=user_id)

       serializer = FollowSerializer(
           data={},
           context={
               "request":request,
                "following":following
            }
       )
       
       serializer.is_valid(raise_exception=True)
       data = serializer.save()
       
       return Response(data)
   
class FollowStatusView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
       user = get_object_or_404(User, id=user_id)
      
       serializer = FollowStatusSerializer(
           instance=user,
           context={"request":request}
       )
       return Response(serializer.data)
    
class MyFollowersView(ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['follower', 'following']

    def get_queryset(self):
        return Follow.objects.filter(
            following=self.request.user
        ).select_related("follower", "following")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = MyFollowerSerializer(
            instance=queryset,
            context={"request":request}
        )
    
        return Response(serializer.data)
       
    
class MyFollowingView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['follower', 'following']

    def get_queryset(self):
        return Follow.objects.filter(
            follower=self.request.user
        ).select_related("follower", "following")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = MyFollowingSerializer(
            instance=queryset,
            context={"request":request}
        )
    
        return Response(serializer.data)
       
        
        
        
    