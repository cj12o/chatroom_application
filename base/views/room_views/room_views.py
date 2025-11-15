from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from asgiref.sync import sync_to_async
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication,BaseAuthentication
from django.contrib.auth.models import User

from base.models import Room,UserProfile,Topic
from ...serializers.room_serializer import RoomSerializer,RoomSerializerForPagination,RoomSerializerForCreation

from ..logger import logger
from ..topic_filter import topicsList
# from .userRecommendation.chroma import getRecommendation

from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100





class UserRecommendation(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    # def get(self,request):
    #     """
    #     fetches data from llm recomm 
    #     """
    #     #Todo:if new user
    #     print(f"REquet:{request.user}")
    #     recom_lst=getRecommendation(request.user.username)
    #     # print(recom_lst)
    #     name_lst=[obj["name"] for obj in recom_lst]
    #     print(name_lst)
    #     rooms=Room.objects.filter(Q(name__in=name_lst))
    #     serializer=RoomSerializer(rooms,many=True)
    #     print(f"✅✅serilizer:{serializer}")
    #     if serializer.data:
    #         return Response({
    #             "rooms":serializer.data,
    #             "reason":[obj["reason"] for obj in recom_lst],
    #             "message":"list of Rooms recommendations"
    #         },status=status.HTTP_200_OK)
    #     else:
    #         return Response({
    #             # "error":serializer.errors,
    #             "message":"error in fetching room recommendations"
    #         },status=status.HTTP_400_BAD_REQUEST)
        
            

class RoomListPagination(PageNumberPagination):
    page_size = 3


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def listRooms(request):
    try:
        paginator=RoomListPagination()
        need=request.data["need"] #need=[parent topic filter:2,search bar specific :1,searchbar random]
        

        qs=None

        if need==1:
            "case when from search bar a prticular romm is selected"
            id=request.data["id"]
            qs=Room.objects.filter(id=id)
        
        elif need==2:
            "case of parent topic filtering "
            topic=request.data["keyword"]
            qs=Room.objects.filter(Q(parent_topic__topic=topic))

        else:
            "random word in search bar so dynamic searching"
            keyword=request.data["keyword"].strip().lower()
            qs=Room.objects.filter(
            Q(name__icontains=keyword)|
            Q(parent_topic__topic__icontains=keyword)|
            Q(author__username__icontains=keyword)|
            Q(tags__icontains=keyword)).order_by("-updated_at","-created_at")

        result_page=paginator.paginate_queryset(qs, request)
        
        serializer=RoomSerializerForPagination(result_page,context={"username":request.user.username},many=True)
        
        return paginator.get_paginated_response(serializer.data)
       
    except Exception as e:
        logger.error(e)
        return Response({
            "ERROR":str(e)
        },status=status.HTTP_400_BAD_REQUEST)
    



class RoomApiview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def get_permissions(self):
        if self.request.method=="GET":
            return []
        else:return [IsAuthenticated()]

    def get_authenticators(self):
        if self.request.method=="GET":
            return []
        else:return [TokenAuthentication()]
    
    #create new Room
    def get(self,request):
        "method returns per room detail"
        try:
            if not request.GET.get('id'):
                return Response({"message":"no id passed"},status=status.HTTP_400_BAD_REQUEST)

            param=request.GET.get('id')
            qs=Room.objects.filter(Q(id=param))
            serializer=RoomSerializer(qs,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":f"Error in getting room {str(e)}"},status=status.HTTP_400_BAD_REQUEST)

   
    def patch(self,request):
        try:
            """
            for room owner  
            """
            data=request.data
            room=Room.objects.get(Q(author__username=request.user.username)&Q(id=data["id"]))
            serializer=RoomSerializerForCreation(data=data,instance=room,partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "roomdata":serializer.data,
                    "message":"Room updated"
                },status=status.HTTP_200_OK)
            
        except Exception as e:    
            logger.error(e)
            return Response({
                "error":str(e),
                "message":"error in Room updation"
            },status=status.HTTP_400_BAD_REQUEST)
    

    def post(self,request):
        try:
            data=request.data
            
            serializer=RoomSerializerForCreation(data=data,context={
                'request':request
            })
            if serializer.is_valid():
                room=serializer.save()
                
            return Response({
                "msg":"room done"
            },status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({
                "msg":"room not created"
            },status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        data=request.data
        room=Room.objects.get(Q(author__username=request.user)&Q(id=data["id"]))
        if room:
            room.delete()
            return Response({
                "message":"Room deleted"
            },status=status.HTTP_200_OK)
        
        return Response({
            "error":"Invalid room",
            "message":"error in Room deletion"
        },status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def getOnlineusers(request,pk):

    # TODO Room filter
    """
    id+name
    get online users 
    """ 
    room=Room.objects.get(id=pk)
    users=room.members.all()
    # if request.GET.get('room_id'):
    #    room_id=int(request.GET.get('room_id'))
    #    room=Room.objects.filter(id=room_id)
    #    onlineUsers=room.room_members.all()
    #    return Response({
    #         "is_online":[user.username for user in onlineUsers]
    #    })
    print(f"users{users}")
    
    return Response({
        "is_online":[[user.username,user.id,UserProfile.objects.get(user__username=user.username).is_online] for user in users]
    })


    
    

    
