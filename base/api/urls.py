from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

from ..views import admin_views as av
from ..views import room_views as rv

urlpatterns=[
    path("user-details/",av.UserApiview.as_view()),
    path("admin-login/",av.LoginApiview.as_view()),
    path("logout/",av.LogoutApiview.as_view()),

    #ROOM VIEWS
    path("rooms/list/",rv.listRooms),
    path("rooms/operations/",rv.RoomApiview.as_view())
]

if settings.DEBUG==True:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

