from django.urls import path
from apps.likes import views
from apps.likes.views import ToggleLikeView

urlpatterns = [
    path("like/post/<int:post_id>/", ToggleLikeView.as_view()),
]

''' full url = like/posts/1/like'''