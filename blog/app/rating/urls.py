from django.urls import path
from app.rating.views import rate_post

urlpatterns = [
    path('rate/', rate_post),
]