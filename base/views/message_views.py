from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authentication import TokenAuthentication,BaseAuthentication
from rest_framework import status
from django.db.models import Q
from rest_framework.decorators import api_view
from django.conf import settings

from ..serializers.message_serializer import MessageSerializerForCreation,MessageSerializer
from ..models.message_model import Message,Vote
from ..models.room_model import Room
from ..logger import logger
from channels.layers import get_channel_layer
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
    

    """post 1 msg"""
    def post(self,request,pk,*args,**kwargs):
        try:
            data=request.data
            #file
            # file=request
            # logging.fatal(f"{file.FILES["file"]}")
            room_id=pk

            author=User.objects.get(id=request.user.id)
            room=Room.objects.get(id=pk)

            context={"request":{"author":author,"room":room}}

            if request.FILES:
                if request.FILES.get("file"):
                    file=request.FILES.get("file")
                    context["request"]["file"]=file
                
                if request.FILES.get("image"):
                    image=request.FILES.get("image")
                    context["request"]["image"]=image
        

            
            if "parent_id" in data:
                print("✅✅parent in")
                parent=Message.objects.get(id=data["parent_id"])
                context["request"]["parent"]=parent

            serializer=MessageSerializer(data=data,partial=False,context=context)
            # print(f"{serializer}")
            
            if serializer.is_valid():
                msg=serializer.save()
                asyncio.run(sendToWs(room_id=msg.room.id,message=msg.message,username=msg.author.username,message_id=msg.id,file_url=msg.file_msg,image_url=msg.images_msg))
                return Response({
                    "message":"posted msg"
                },status=status.HTTP_200_OK)
            


        except Exception as e:
            logger.fatal(f"ERROR in message view:{str(e)}")
            return Response({
                # "error":serializer.errors,
                "message":"error in posting msg"
            },status=status.HTTP_400_BAD_REQUEST)   
        

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
         


