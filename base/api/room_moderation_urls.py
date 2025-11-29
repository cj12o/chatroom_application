from django.urls import path
from ..views.moderator import moderator_views as mv

urlpatterns=[
    path("mod_room_lst/",mv.getRoomsForModeration),
    path("messages/<int:pk>/",mv.ModerationMessageApiview.as_view()),
]