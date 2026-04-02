# app/follow/urls.py

from django.urls import path
from app.follow.views import FollowStatusView, ToggleFollowView, MyFollowersView, MyFollowingView

urlpatterns = [
    path("follow/user/<int:user_id>/", ToggleFollowView.as_view()),
    path("follow-status/user/<int:user_id>/", FollowStatusView.as_view()),
    path("followers/", MyFollowersView.as_view()),
    path("followings/", MyFollowingView.as_view()),
]