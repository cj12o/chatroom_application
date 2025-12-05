from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.db.models import Q
from django.conf import settings

from ..serializers.message_serializer import MessageSerializerForCreation,MessageSerializer
from ..models.message_model import Message
from ..models.room_model import Room
from ..logger import logger
from channels.layers import get_channel_layer
from ..threadPool import ThreadPoolManager
import asyncio

def helper(id:int,lst:list)->list:
    "recursion based method to give hierarchy of messages in nested way"
    try:
        message=Message.objects.get(id=id)
        serializer=MessageSerializerForCreation(message)
        
        lst.append(serializer.data if serializer.data else {})

        if message.parent_message.all():   
            for m in message.parent_message.all():
                helper(m.id,lst[len(lst)-1]["children"])
    except Exception as e:
        logger.error(e)


def _build_absolute_media_url(resource):
    if not resource:
        return None
    return f"{settings.SITE_BASE_URL}{resource.url}"


async def sendToWs(room_id:int,message:str,username:str,message_id:int,file_url,image_url):
    channel_layer=get_channel_layer()
    file_path=_build_absolute_media_url(file_url)
    image_path=_build_absolute_media_url(image_url)
    if file_url and image_url:
        await channel_layer.group_send(
            f"room_{room_id}",
            {
                "type": "chat_message",
                "task":"chat",
                "message":message, 
                "file_url":file_path,
                "image_url":image_path, 
                "parent":None,
                "username":username,
                "message_id":message_id
                # "status": True
            }
        )
    elif file_url:
        await channel_layer.group_send(
            f"room_{room_id}",
            {
                "type": "chat_message",
                "task":"chat",
                "message":message, 
                "file_url":file_path,
                "image_url":None, 
                "parent":None,
                "username":username,
                "message_id":message_id
                # "status": True
            }
        )
    else:
        await channel_layer.group_send(
            f"room_{room_id}",
            {
                "type": "chat_message",
                "task":"chat",
                "message":message, 
                "file_url":None,
                "image_url":image_path, 
                "parent":None,
                "username":username,
                "message_id":message_id
                # "status": True
            }
        )

class MessageApiview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    
    def get_permissions(self):
        if self.request.method=="GET":
            return [AllowAny()]
        else:
            return [IsAuthenticated()]


    def post(self, request, pk, *args, **kwargs):
        try:
            author = request.user
            room = Room.objects.get(id=pk)

            payload = {}

            
            payload["message"] = request.data.get("message", "")

            if request.FILES.get("file"):
                payload["file_msg"] = request.FILES["file"]

            if request.FILES.get("image"):
                payload["images_msg"] = request.FILES["image"]

            
            if request.data.get("parent_id"):
                payload["parent"] = Message.objects.get(id=request.data["parent_id"])

            
            serializer = MessageSerializer(
                data=payload,
                context={"author": author, "room": room}
            )

            serializer.is_valid(raise_exception=True)
            msg = serializer.save()

            # Send event to websocket
            ThreadPoolManager.get().submit(lambda :asyncio.run(sendToWs(
                room_id=msg.room.id,
                message=msg.message,
                username=msg.author.username,
                message_id=msg.id,
                file_url=msg.file_msg,
                image_url=msg.images_msg
            )))

            return Response({"message": "posted msg"}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in posting message: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self,request,pk):
        messages=Message.objects.filter(Q(parent=None))
    
        lst=[]
        if pk!=None:
            messages=messages.filter(Q(room__id=pk))
        for m in messages:
            helper(m.id,lst)
        

        return Response({
            "messages":lst
        },status=status.HTTP_200_OK)
        
   
    """pk is message id"""
    def delete(self,request,pk):
        try:
            id=request.GET.get('id')
            print(f"ID:{id}")
            msg=Message.objects.get(Q(author__id=request.user.id) & Q(room__id=pk) & Q(id=id))
            if msg:
                msg.delete()
                return Response({
                    "message":"deleted message"
                },status=status.HTTP_200_OK) 
            else: raise Exception("no msg with such id")
        except Exception as e:
            logger.error(e)
            return Response({
                "error":str(e),
                "message":"error in deleting msg"
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
         


