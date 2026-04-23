from django.urls import path
from apps.ratings.views import RatePostView

urlpatterns = [
    path('rates/', RatePostView.as_view()),
]