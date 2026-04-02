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
from app.post.serializers import  PostSerializer, SearchSerializer
from django.db.models import Q
from app.comment.serializers import CommentSerializer
from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()

class PostViewSet(ModelViewSet):

    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_Fields = ['is_private', 'user_username']
    search_fields = ['title', 'content', 'user__username']

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    # ======================
    # 🔥 MAIN LOGIC
    # ======================
    def list(self, request, *args, **kwargs):

        user_id = request.query_params.get("user_id")

        # ======================
        # 👉 PROFILE POSTS
        # ======================
        if user_id:
            target_user = get_object_or_404(User, id=user_id)

            # 🔐 PRIVATE ACCOUNT CHECK (user-level)
            if target_user.is_private:

                if not request.user.is_authenticated:
                    return Response({"message": "Account is private"}, status=403)

                is_following = Follow.objects.filter(
                    follower=request.user,
                    following=target_user
                ).exists()

                if not is_following and request.user != target_user:
                    return Response({"message": "Account is private"}, status=403)

            # 🔥 POST-LEVEL FILTER
            if request.user.is_authenticated:
                posts = Post.objects.filter(
                    user=target_user
                ).filter(
                    Q(is_private=False) |  # public posts
                    Q(user=request.user) |  # own posts
                    Q(user__followers__follower=request.user)  # following
                ).distinct()
            else:
                posts = Post.objects.filter(
                    user=target_user,
                    is_private=False
                )

        # ======================
        # 👉 FEED
        # ======================
        else:

            if request.user.is_authenticated:

                following_ids = Follow.objects.filter(
                    follower=request.user
                ).values_list("following_id", flat=True)

                posts = Post.objects.filter(
                    Q(is_private=False) |
                    Q(user=request.user) |
                    Q(user__id__in=following_ids)
                ).distinct().order_by("-created_at")

            else:
                posts = Post.objects.filter(
                    is_private=False
                ).order_by("-created_at")

        posts = posts.order_by("-created_at")

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    # ======================
    # CREATE
    # ======================
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ======================
    # UPDATE
    # ======================
    def perform_update(self, serializer):
        post = self.get_object()
        if post.user != self.request.user:
            raise PermissionDenied("Not allowed")
        serializer.save()

    # ======================
    # DELETE
    # ======================
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Not allowed")
        instance.delete()
        
    
class SearchView(APIView):

    def get(self, request):

        serializer = SearchSerializer(data=request.GET)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        query = serializer.validated_data["query"]

        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__username__icontains=query)
        )

        comments = Comment.objects.filter(
            Q(text__icontains=query)
        )

        return Response({
            "posts": PostSerializer(posts, many=True).data,
            "comments": CommentSerializer(comments, many=True).data
        })  