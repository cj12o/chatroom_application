from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authentication import TokenAuthentication,BaseAuthentication
from rest_framework import status
from django.db.models import Q
from rest_framework.decorators import api_view

from ..serializers.message_serializer import MessageSerializerForCreation,MessageSerializer
from ..models.message_model import Message,Vote
from ..models.room_model import Room



def helper(id:int,lst:list):
    message=Message.objects.get(id=id)
    votes=Vote.objects.filter(Q(message__id=message.id))
    upvotes=votes.filter(Q(vote=1))
    downvotes=votes.filter(Q(vote=-1))
    d={"id":message.id,"author":message.author.username,"message":message.message,"upvotes":len(upvotes),"downvotes":len(downvotes),"children":[]}

    
    lst.append(d)
    # dct[id]=d
    try:
        # print("children:",message.parent_message.all())
        if message.parent_message.all():   
            for m in message.parent_message.all():
                # print(f"❌❌Child if:{m}")
                helper(m.id,lst[len(lst)-1]["children"])
    except Exception as e:
        # dct[id]={}
        print(f"❌❌Error:{e}")
        # return {}
    
       


class MessageApiview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    
    def get_permissions(self):
        if self.request.method=="GET":
            return [AllowAny()]
        else:
            return [IsAuthenticated()]
    

    """post 1 msg"""
    def post(self,request,pk):
        data=request.data
        room_id=pk

        author=User.objects.get(id=request.user.id)
        room=Room.objects.get(id=pk)
        context={"request":{"author":author,"room":room}}

        if "parent_id" in data:
            print("✅✅parent in")
            parent=Message.objects.get(id=data["parent_id"])
            context["request"]["parent"]=parent

        serializer=MessageSerializer(data=data,partial=False,context=context)
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
        messages=Message.objects.filter(Q(parent=None))
        # dct={}
        lst=[]
        for m in messages:
            helper(m.id,lst)
        # lst=[v for k,v in dct.items()]

        print(f"✅✅Final dcyt:{lst}")



        return Response({
            "messages":lst
        },status=status.HTTP_200_OK)
   
    """pk is message id"""
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
    
    # def put(self,request,pk):
    #     data=request.data
    #     msg=Message.objects.get(id=pk)
    #     serializer=MessageSerializer(instance=msg,data=data,partial=False)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({
    #             "msg_lst":serializer.data,
    #             "message":"updated msg"
    #         },status=status.HTTP_200_OK)

    #     return Response({
    #         "error":serializer.errors,
    #         "message":"error in updating msg"
    #     },status=status.HTTP_400_BAD_REQUEST)       

