from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.comment.views import CommentViewSet

router = DefaultRouter()
router.register('comment', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),

    # ✅ nested route (NEW)
    path('comment/post/<int:post_id>/', CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
]