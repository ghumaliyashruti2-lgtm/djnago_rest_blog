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
import logging

logger = logging.getLogger(__name__)

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
            
        if self.action == "list":
            return queryset.filter(parent__isnull=True)

        return queryset

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
        logger.debug(f"user {self.request.user} trying to comment on post {post}")
        comment = serializer.save(post=post, user=self.request.user)
        logger.info(f"Comment created: user={self.request.user}, post={post}, comment_id={comment.id}")
        
    # ======================
    # REPLY COMMENT
    # ======================
    @action(detail=False, methods=["POST"])
    def reply(self, request):
        logger.debug(f"User {request.user.username} is attempting to reply")
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        logger.info(f"Reply created by user={request.user.username} on comment_id={comment.id}")
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
        logger.debug(f"User {request.user} try to delete comment {self.comment.id}")
        super().destroy(request, *args, **kwargs)
        logger.info(f"User {request.user} successfully delete comment {self.comment.id}")
        return Response({"msg": "Comment deleted"})
    
    # ==========================
    # GET USER PROFILE 
    # ==========================

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated], url_path="users/profile")
    def user_profile(self, request, pk=None):
        logger.debug(f"user {request.user} is requesting to show proifle owner of comment id ={pk}")
        
        try:
            comment = self.get_object()
        except Exception as e:
            logger.error(f"Comment not found: id={pk}, error={str(e)}")
            raise
        
        user = comment.user
        
        logger.info(
            f"user {request.user} fetched profile {user} owner of comment_id={comment.id}"
        )

        serializer = ProfileSerializer(user)
        return Response(serializer.data)
