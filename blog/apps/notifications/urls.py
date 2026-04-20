from django.urls import path
from apps.notifications.views import (NotificationListView,
    NotificationMarkReadView,
    NotificationDeleteView,
    UnreadCountView)

urlpatterns = [
    path("notification/", NotificationListView.as_view()),
    path("notification/<int:pk>/read/", NotificationMarkReadView.as_view()),
    path("notification/<int:pk>/delete/", NotificationDeleteView.as_view()),
    path("notification/unread-count/", UnreadCountView.as_view()),
]

''' full url = notification/notifications/1/read/ | delete/
             = notification/notifications/unread-count/'''