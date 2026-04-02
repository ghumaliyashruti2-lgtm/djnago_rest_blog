from django.urls import path,include
from app.post.views import PostViewSet, SearchView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('post', PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', SearchView.as_view(), name='search'),
]

''' full url = post/posts/1/ for update | delete | get  '''