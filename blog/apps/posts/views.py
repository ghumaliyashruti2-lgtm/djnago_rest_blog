# Create your views here.
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from apps.posts.models import Post
from django_filters.rest_framework import DjangoFilterBackend 
from django.contrib.auth import get_user_model
from apps.posts.serializers import  PostSerializer,DeleteSerializer
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from django_filters import rest_framework as filter
from rest_framework.filters import SearchFilter, OrderingFilter
from blog.permission import IsOwnerOrReadOnly
from blog.pagination import NumPagination
from rest_framework import status

User = get_user_model()

class postfilter(filter.FilterSet):
    post_title = filter.CharFilter(field_name="title", lookup_expr="iexact")
    users = filter.NumberFilter(field_name="user", lookup_expr="gt") # order on users if user id 10 > gt ..
    user = filter.ModelChoiceFilter(queryset=User.objects.all()) # get post info based o user 
    multiple_user = filter.ModelMultipleChoiceFilter(field_name="user__id", to_field_name ="id", queryset= User.objects.all()) # select multiple user and get post info


    
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    pagination_class = NumPagination
    
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    #filterset_fields = ["title"]
    filterset_class = postfilter
    #search_fields = ["title", "content", "users__username"]
    ordering_fields ="__all__"

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        self.queryset = PostSerializer.get_filtered_posts(request)
        return super().list(request, *args, **kwargs)

    #def perform_create(self, serializer):
    #    serializer.save(user=self.request.user)
        
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    #def perform_update(self, serializer):
    #   PostSerializer.validate_post_owner(self.request.user, self.get_object())
    #   serializer.save()
        
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={"200":DeleteSerializer,},
        operation_id="User Post DELETE"
    )
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return Response({"msg": "Your data has been deleted"}, status=status.HTTP_200_OK)
        
        
        
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_posts(self, request, *args, **kwargs):
        self.get_queryset = lambda: PostSerializer.get_user_posts(request.user)
        return super().list(request, *args, **kwargs)


    @action(detail=True, methods=['get'], url_path='user')
    def get_post_owner(self, request, pk=None):
        post = self.get_object()
        data = PostSerializer.get_user_stats(post.user)
        return Response(data)

