from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication,BaseAuthentication
from django.contrib.auth.models import User

from ..models.room_model import Room
from ..serializers.room_serializer import RoomSerializer,RoomSerializerForCreation


@api_view(['GET'])
def listRooms(request):
    #write serilizer to limit fields
    qs=Room.objects.all()
    

    if request.GET.get('search'):
        param=request.GET.get('search')
        print(f"Params:{param}")

        qs=qs.filter(Q(author__username__icontains=param)|Q(name__icontains=param)|Q(description__icontains=param)|Q(topic__icontains=param))
    

    serializer=RoomSerializer(qs,many=True)
    print(f"✅✅Serializers:{serializer.data}")
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
            serializer.save()
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
    
    
        
    

    
