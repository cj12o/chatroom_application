from ..views import room_edit_views as rev
from django.urls import path


urlpatterns=[
    path("room_edit/<int:pk>/",rev.RoomEditView.as_view())    
]