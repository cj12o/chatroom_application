from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication,BaseAuthentication
from rest_framework import status
from django.db.models import Q

from ..serializers.message_serializer import MessageSerializerForCreation,MessageSerializer
from ..models.message_model import Message
from ..models.room_model import Room

class MessageApiview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication,BaseAuthentication]

    def post(self,request,pk):
       
        data=request.data
        # room_id=request.POST.get('room_id')
        room_id=pk

        user=User.objects.get(id=request.user.id)
        room=Room.objects.get(id=pk)
        serializer=MessageSerializer(data=data,partial=False,context={""
        "request":{
            "user":user,
            "room":room
        }})
        # print(f"{serializer}")
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "msg_lst":serializer.data,
                "message":"posted msg"
            },status=status.HTTP_200_OK)

        return Response({
            "error":serializer.errors,
            "message":"error in posting msg"
        },status=status.HTTP_400_BAD_REQUEST)   
    

    def get(self,request,pk):
        print(f"✅✅Room id=>{pk}")
        msg=Message.objects.filter(Q(room__id=pk))
        
        print(f"✅✅messag qs:{msg}")

        if not msg:
            return Response({
                "msg_lst":"empty room",
                "message":"error in posting msg"
            },status=status.HTTP_200_OK) 
        

        serializer=MessageSerializerForCreation(msg,many=True)

        if serializer.data:
            return Response({
                "msg_lst":serializer.data,
                "message":"all msg"
            },status=status.HTTP_200_OK)

        return Response({
            "error":serializer.errors,
            "message":"error in posting msg"
        },status=status.HTTP_400_BAD_REQUEST) 
   

    def delete(self,request,pk):
        # pk:msgid
        #if room is rmpty
        msg=Message.objects.get(Q(author__id=request.user.id) & Q(id=pk))
        if msg:
            msg.delete()
            return Response({
                "message":"deleted message"
            },status=status.HTTP_200_OK) 
        return Response({
            "error":"Invalid room or author",
            "message":"error in posting msg"
        },status=status.HTTP_400_BAD_REQUEST) 
    
    def patch(self,request,pk):
        data=request.data
        msg=Message.objects.get(id=pk)
        serializer=MessageSerializer(instance=msg,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "msg_lst":serializer.data,
                "message":"updated msg"
            },status=status.HTTP_200_OK)

        return Response({
            "error":serializer.errors,
            "message":"error in updating msg"
        },status=status.HTTP_400_BAD_REQUEST)       
    
    def put(self,request,pk):
        data=request.data
        msg=Message.objects.get(id=pk)
        serializer=MessageSerializer(instance=msg,data=data,partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "msg_lst":serializer.data,
                "message":"updated msg"
            },status=status.HTTP_200_OK)

        return Response({
            "error":serializer.errors,
            "message":"error in updating msg"
        },status=status.HTTP_400_BAD_REQUEST)       
