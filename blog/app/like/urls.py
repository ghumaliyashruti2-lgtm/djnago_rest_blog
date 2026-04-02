from django.urls import path
from app.like import views
from app.like.views import ToggleLikeView

urlpatterns = [
    path("like/post/<int:post_id>/", ToggleLikeView.as_view()),
]

''' full url = like/posts/1/like'''