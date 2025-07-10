from django.urls import path
from . import views

urlpatterns = [
    path('mark-seen/', views.mark_notifications_seen, name='mark_notifications_seen'),
]
