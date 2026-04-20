# app/follow/urls.py

from django.urls import path
from apps.follows.views import FollowStatusView, MyFollowersView, ToggleFollowView, MyFollowingView

urlpatterns = [
    path("follow/user/<int:user_id>/", ToggleFollowView.as_view()),
    path("follow-status/user/<int:user_id>/", FollowStatusView.as_view()),
    path("followers/", MyFollowersView.as_view()),
    path("followings/", MyFollowingView.as_view()),
    
]