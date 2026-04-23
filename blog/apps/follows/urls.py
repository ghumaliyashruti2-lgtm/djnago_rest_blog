# app/follow/urls.py

from django.urls import path
from apps.follows.views import FollowStatusView, MyFollowersView, ToggleFollowView, MyFollowingView

urlpatterns = [
    path("follows/users/<int:user_id>/", ToggleFollowView.as_view()),
    path("follows/follow-status/users/<int:user_id>/", FollowStatusView.as_view()),
    path("follows/followers/", MyFollowersView.as_view()),
    path("follows/followings/", MyFollowingView.as_view()),
    
]