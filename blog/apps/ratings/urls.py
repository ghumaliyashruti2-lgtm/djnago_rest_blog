from django.urls import path
from apps.ratings.views import RatePostView

urlpatterns = [
    path('rate/', RatePostView.as_view()),
]