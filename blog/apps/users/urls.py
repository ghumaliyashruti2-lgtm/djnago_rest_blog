from django.urls import path,include
from rest_framework.routers import DefaultRouter
from apps.users.views import AuthViewSet
router = DefaultRouter()
router.register("users", AuthViewSet, basename="users")

urlpatterns = [
    path('',include(router.urls)), 
]




