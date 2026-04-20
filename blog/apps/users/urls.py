from django.urls import path,include
from rest_framework.routers import DefaultRouter
from apps.users.views import AuthViewSet
router = DefaultRouter()
router.register("user", AuthViewSet, basename="user")

urlpatterns = [
    path('',include(router.urls)), 
]




