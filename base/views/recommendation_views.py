from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

from ..models.room_model import Room
from ..models.recommendation_model import Recommend
from ..serializers.recommendation_serializers import RecommndationSerializer

# from .userRecommendation.chroma import getRecommendation


def deleteOldRecom(user_id:int):
    try:
        print(f"✅✅userId delete :{user_id}")
        oldRecomm=Recommend.objects.filter(user__id=user_id)
        oldRecomm.delete()

    except Exception as e:
        pass


class saveRecommendation(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]


    #TODO sesializer  , delet prev ones
    # def post(self,request):
        # """
        # purpose ->gets recom from llm 
        # and saves in db
        # """
        # try:
        #     # delete_old_recomm
        #     deleteOldRecom(request.user.id)

        #     sesh_id=request.data["sessionId"]
        #     recom_lst=getRecommendation(request.user.username)
        
        #     user=User.objects.get(id=request.user.id)
        #     print(f"✅✅Recoom list:{recom_lst}")

        #     for obj in recom_lst:
        #         #room is safer as llm may give id as str
        #         room=Room.objects.get(name=obj["name"])
        #         hist=Recommend.objects.create(user=user,room=room,reason=obj["reason"],session=sesh_id)
            
            
         
        
        #     return Response({
        #         "message":"saved recomm in db"
        #     },status=status.HTTP_200_OK)
        # except Exception as e:
        #     return Response({
        #         "error":str(e),
        #         "message":"error in saving recomm in db"
        #     },status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):
        """
        purpose= returns recommendation to homepage
        """
        qs=Recommend.objects.filter(Q(user__username=request.user.username))
        serializer=RecommndationSerializer(qs,context={"user_auth_status":request.user.is_authenticated,"username":request.user.username if request.user.is_authenticated else ""},many=True)
        if serializer.data:
            return Response({
                "rooms":serializer.data
            },status=status.HTTP_200_OK)
        
        return Response({
            "error":serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)


