from ..views.room_views import room_stats_views as rev
from django.urls import path


urlpatterns=[
    path("room_user_stats/<int:pk>/",rev.getStats)    
]