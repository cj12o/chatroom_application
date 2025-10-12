from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

from ..views import admin_views as av
from ..views import room_views as rv
from ..views import message_views as mv
# from ..views import reaction_views as rcv
from ..views import emoji_views as ev
from ..views import profile_views as pv
from ..views import topic_views as tv
from ..views.userRecommendation import chroma as cv
from ..views import history_views as hv

from ..views.llm import tools 

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
    # path("messages/<int:pk>/reaction/<int:q>/",rcv.ReactionApiview.as_view()),

    ##emoji views
    # path("messages/<int:pk>/emoji/<int:q>/",ev.EmojiApiview.as_view()),


    ##userprofile view
    path("userprofile/<str:q>/",pv.UserProfileApiview.as_view()),


    ##topic view

    path("topics/",tv.TopicApiview.as_view()),

    # path("prediction/",cv.topk),

    ##history
    path("sethistory/",hv.setHistory),

    # path("tester/",tools.get_userHistory)
    path("is_online/<int:pk>/",rv.getOnlineusers),
    

]



