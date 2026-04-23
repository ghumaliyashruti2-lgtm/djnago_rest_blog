from django.urls import path
from apps.notifications.views import (NotificationListView,
    NotificationMarkReadView,
    NotificationDeleteView,
    UnreadCountView)

urlpatterns = [
    path("notifications/", NotificationListView.as_view()),
    path("notifications/<int:pk>/read/", NotificationMarkReadView.as_view()),
    path("notifications/<int:pk>/", NotificationDeleteView.as_view()),
    path("notifications/unread-count/", UnreadCountView.as_view()),
]

''' full url = notification/notifications/1/read/ | delete/
             = notification/notifications/unread-count/'''