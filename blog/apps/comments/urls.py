from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.comments.views import CommentViewSet

router = DefaultRouter()
router.register('comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),

    path('comments/posts/<int:post_id>/', CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
]