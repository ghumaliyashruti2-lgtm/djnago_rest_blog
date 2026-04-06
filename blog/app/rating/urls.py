from django.urls import path
from app.rating.views import RatePostView

urlpatterns = [
    path('rate/', RatePostView.as_view()),
]