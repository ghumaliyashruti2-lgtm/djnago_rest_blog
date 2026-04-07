from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from app.user.serializers import ProfileSerializer
from django_filters.rest_framework import DjangoFilterBackend

from app.comment.models import Comment
from app.post.models import Post
from app.comment.serializers import (
    CommentSerializer,
    CreateCommentSerializer,
    ReplyCommentSerializer,
)
from app.notification.views import create_notification


class CommentViewSet(ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'user', 'parent']
    search_fields = ["text"]

    def get_permissions(self):
        if self.action in ["create", "reply", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    #  Dynamic serializer
    def get_serializer_class(self):
        if self.action == "create":
            return CreateCommentSerializer
        elif self.action == "reply":
            return ReplyCommentSerializer
        return CommentSerializer

    # ======================
    # CREATE COMMENT
    # ======================
    def create(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs.get("post_id"))

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request, "post": post}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        return Response({
            "message": "Comment added",
            "comment_id": comment.id
        }, status=201)

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
    # LIST COMMENTS (NOW USING FILTER)
    # ======================
    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        post_id = self.kwargs.get("post_id")
        if post_id:
            queryset = queryset.filter(post_id=post_id)

        queryset = queryset.filter(parent__isnull=True)

        serializer = CommentSerializer(queryset, many=True)
        return Response({"comments": serializer.data})

    # ======================
    # UPDATE COMMENT
    # ======================
    def update(self, request, *args, **kwargs):
        comment = self.get_object()

        serializer = UpdateCommentSerializer(
            comment,
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Comment updated"})
        

    # ======================
    # DELETE COMMENT
    # ======================
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()

        serializer = DeleteCommentSerializer(
            context={"request": request}
        )
        serializer.delete(comment)

        return Response({"message": "Comment deleted"})
    
    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated], url_path="user/profile")
    def user_profile(self, request, pk=None):
        comment = self.get_object()
        user = comment.user

        serializer = ProfileSerializer(user)
        return Response(serializer.data)