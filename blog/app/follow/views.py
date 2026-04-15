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
from drf_yasg.utils import swagger_auto_schema
User = get_user_model()


class ToggleFollowView(CreateModelMixin, DestroyModelMixin, GenericAPIView):

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer 
    
    
    @ swagger_auto_schema(
        operation_description= "Follow user",
        request_body = FollowSerializer,
        response = {200:FollowSerializer,},
        operation_id = "Follow POST"
    )


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
    serializer_class = FollowStatusSerializer
        
    @ swagger_auto_schema(
        operation_description="check user follow or not",
        response = {200:FollowStatusSerializer,},
        operation_id = "Follow GET"
    )

    
    def get(self, request, user_id):
       user = get_object_or_404(User, id=user_id)
       if request.user == user:
            return Response(
                {"error": "You cannot follow yourself"},
                status=400
            )
       serializer = FollowStatusSerializer(
           instance=user,
           context={"request":request}
       )
       return Response(serializer.data)
    
class MyFollowersView(ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['follower', 'following']
    serializer_class = MyFollowerSerializer 

    def get_queryset(self):
        return Follow.objects.filter(
            following=self.request.user
        ).select_related("follower", "following")
        
            
    @ swagger_auto_schema(
        operation_description="followers user list",
        response = {200:MyFollowerSerializer(many=True),},
        operation_id = "Follow List"
    )


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
    serializer_class = MyFollowingSerializer

    def get_queryset(self):
        return Follow.objects.filter(
            follower=self.request.user
        ).select_related("follower", "following")
        
    @ swagger_auto_schema(
        operation_description="following user list",
        response = {200:MyFollowingSerializer(many=True),},
        operation_id = "Follow List"
    )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = MyFollowingSerializer(
            instance=queryset,
            context={"request":request}
        )
        return Response(serializer.data)
       
        
        
        
    