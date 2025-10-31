from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

from ..views import admin_views as av
from ..views import room_views as rv
from ..views import message_views as mv
from ..views import profile_views as pv
from ..views import topic_views as tv
from ..views.userRecommendation import chroma as cv
from ..views import history_views as hv

from ..views import vote_views as vv

from ..views.agent import agent_view as agv


urlpatterns=[
    path("user-details/",av.UserApiview.as_view()),
    path("admin-login/",av.LoginApiview.as_view()),
    path("logout/",av.LogoutApiview.as_view()),
    path("signup/",av.SignUpApiview.as_view()),

    #ROOM VIEWS
    path("rooms/list/",rv.listRooms),
    #User recommendation
    # path("rooms/recommend/",rv.UserRecommendation.as_view()),
    #recomm save
    # path("rooms/saveRecomm/",rev.saveRecommendation.as_view()),

    path("rooms/operations/",rv.RoomApiview.as_view()),

    #message views
    path("rooms/<int:pk>/messages/",mv.MessageApiview.as_view()),
    

    ##userprofile view
    path("userprofile/<str:q>/",pv.UserProfileApiview.as_view()),


    ##topic view

    path("topics/",tv.TopicApiview.as_view()),

    # path("prediction/",cv.topk),

    ##history
    path("sethistory/",hv.setHistory),

    # path("tester/",tools.get_userHistory)
    path("is_online/<int:pk>/",rv.getOnlineusers),
    
    #vote path temp
    path("votes/<int:pk>/",vv.voteApiview.as_view()),


    #testing agent 
    path("triggeragent/",agv.AgentApiviews.as_view())
  
]



