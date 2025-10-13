from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication,BaseAuthentication
from django.contrib.auth.models import User

from ..models.room_model import Room
from ..models.userprofile_model import UserProfile
from ..serializers.room_serializer import RoomSerializer,RoomSerializerForCreation
# from .userRecommendation.chroma import collection


@api_view(['POST'])
def listRooms(request):
    """
    Purpose->return all rooms list
    Input->1){} or {"topic":" "} returns full list
           2){"topic":"parent_topic"} returns filtered

    attached->home page
    """

    # write serilizer to limit fields
    qs=Room.objects.all()

    ##FOR PARENT TOPIC FILTERING
    if "topic" in request.data and request.data["topic"].strip()!="":
        topic=request.data["topic"]
        qs=qs.filter(Q(parent_topic__topic=topic))
        # print(f"QS:{qs}")
        if len(qs)<1:
            return Response({
            "rooms":[],
            "message":"list of Rooms"
        },status=status.HTTP_200_OK)
        
    """for specific room"""

    if request.GET.get('id'):
        param=request.GET.get('id')

        qs=qs.filter(Q(id=param))
    

    serializer=RoomSerializer(qs,many=True)
    # print(f"✅✅Serializers:{serializer.data}")
    if len(serializer.data)<1:
        return Response({
            "message":"No matching keywords"
        },status=status.HTTP_400_BAD_REQUEST)

    if serializer.data:
        # print(f"✅✅Serializers:{serializer}")
        return Response({
            "rooms":serializer.data,
            "message":"list of Rooms"
        },status=status.HTTP_200_OK)
    
    return Response({
        "message":"error in getting room list",
        "error":serializer.errors
    },status=status.HTTP_400_BAD_REQUEST)


class RoomApiview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication,BaseAuthentication]
    #create new Room
    def post(self,request):
        data=request.data
        print(f"User{request.user}")
        user=User.objects.get(username=request.user)
        serializer=RoomSerializerForCreation(data=data,context={
            'request':user
        })
        if serializer.is_valid():
            room=serializer.save()
            if "moderator" in data:
                for moderator in data["moderator"]:
                    mod=User.objects.get(username=moderator)
                    room.moderator.add(mod)
            else:
                room.moderator.add(user)
            room.save()
            print(f"Serializer data{serializer.data}")

            #add to db
            # collection.add(
            #     ids=["90"],
            #     documents=[
            #         f"name={serializer.data["name"]} description={serializer.data["description"]}" 
            #     ]
            # )


            return Response({
                "roomdata":serializer.data,
                "message":"Room created"
            },status=status.HTTP_200_OK)
        
        return Response({
            "error":serializer.errors,
            "message":"error in Room creation"
        },status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request):
        data=request.data
        room=Room.objects.get(Q(author__username=request.user)&Q(id=data["id"]))
        serializer=RoomSerializerForCreation(data=data,instance=room,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "roomdata":serializer.data,
                "message":"Room updated"
            },status=status.HTTP_200_OK)
        
        return Response({
            "error":serializer.errors,
            "message":"error in Room updation"
        },status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request):
        data=request.data
        room=Room.objects.get(Q(author__username=request.user)&Q(id=data["id"]))
        serializer=RoomSerializerForCreation(data=data,instance=room,partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "roomdata":serializer.data,
                "message":"Room updated"
            },status=status.HTTP_200_OK)
        
        return Response({
            "error":serializer.errors,
            "message":"error in Room updation"
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


    
    

    
