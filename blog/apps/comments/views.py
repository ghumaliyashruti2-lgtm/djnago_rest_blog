from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.users.serializers import ProfileSerializer
from django_filters.rest_framework import DjangoFilterBackend
from apps.comments.models import Comment
from apps.posts.models import Post
from apps.comments.serializers import (
    CommentSerializer,
    CreateCommentSerializer,
    ReplyCommentSerializer,
    UpdateCommentSerializer
)
from apps.notifications.views import create_notification
from blog.permission import IsOwnerOrReadOnly
from blog.pagination import NumPagination

class CommentViewSet(ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = NumPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'user', 'parent']
    search_fields = ["text"]

    def get_permissions(self):
        if self.action in ["create", "reply", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(),IsOwnerOrReadOnly()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()

        post_id = self.kwargs.get("post_id")
        if post_id:
            queryset = queryset.filter(post_id=post_id)

        return queryset.filter(parent__isnull=True)

    #  Dynamic serializer
    def get_serializer_class(self):
        if self.action == "create":
            return CreateCommentSerializer
        elif self.action == "reply":
            return ReplyCommentSerializer
        elif self.action in ["update", "partial_update"]:
            return UpdateCommentSerializer
        return CommentSerializer

    # ======================
    # CREATE COMMENT
    # ======================
    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        serializer.save(post=post, user=self.request.user)
        
    # ======================
    # REPLY COMMENT
    # ======================
    @action(detail=False, methods=["POST"])
    def reply(self, request):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        return Response({
            "message": "Reply added",
            "comment_id": comment.id
        }, status=201)
        
    # ======================
    # UPDATE COMMENT
    # ======================
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
        

    # ======================
    # DELETE COMMENT
    # ======================
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"msg": "Comment deleted"})

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated], url_path="user/profile")
    def user_profile(self, request, pk=None):
        comment = self.get_object()
        user = comment.user

        serializer = ProfileSerializer(user)
        return Response(serializer.data)