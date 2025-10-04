from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

from ..views import admin_views as av
from ..views import room_views as rv
from ..views import message_views as mv
from ..views import reaction_views as rcv
from ..views import emoji_views as ev

urlpatterns=[
    path("user-details/",av.UserApiview.as_view()),
    path("admin-login/",av.LoginApiview.as_view()),
    path("logout/",av.LogoutApiview.as_view()),
    path("signup/",av.SignUpApiview.as_view()),

    #ROOM VIEWS
    path("rooms/list/",rv.listRooms),
    path("rooms/operations/",rv.RoomApiview.as_view()),

    #message views
    path("rooms/<int:pk>/messages/",mv.MessageApiview.as_view()),
    ##reaction views
    path("messages/<int:pk>/reaction/<int:q>/",rcv.ReactionApiview.as_view()),

    ##emoji views
    path("messages/<int:pk>/emoji/<int:q>/",ev.EmojiApiview.as_view()),

]

if settings.DEBUG==True:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

