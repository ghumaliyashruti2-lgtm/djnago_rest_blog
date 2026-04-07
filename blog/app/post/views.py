# Create your views here.
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView, PermissionDenied
from django.shortcuts import get_object_or_404
from app.post.models import Post
from app.follow.models import Follow
from app.comment.models import Comment
from django.contrib.auth import get_user_model
from app.post.serializers import  PostSerializer
from app.comment.serializers import CommentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from app.like.models import Like

User = get_user_model()

class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        posts = PostSerializer.get_filtered_posts(request)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        PostSerializer.validate_post_owner(self.request.user, self.get_object())
        serializer.save()

    def perform_destroy(self, instance):
        PostSerializer.validate_post_owner(self.request.user, instance)
        instance.delete()
        
        
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        posts = PostSerializer.get_user_posts(request.user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='user')
    def get_post_owner(self, request, pk=None):
        post = self.get_object()
        data = PostSerializer.get_user_stats(post.user)
        return Response(data)

    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)')
    def get_user_by_username(self, request, username=None):
        data = PostSerializer.get_user_stats_by_username(username)
        return Response(data)