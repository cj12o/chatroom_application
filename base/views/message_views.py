from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authentication import TokenAuthentication,BaseAuthentication
from rest_framework import status
from django.db.models import Q


from ..serializers.message_serializer import MessageSerializerForCreation,MessageSerializer
from ..models.message_model import Message
from ..models.room_model import Room



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
    

    """get all message  {{base}}rooms/2/messages/?search=4 (specific also)"""
    def get(self,request,pk):
        
        # print(f"✅✅Room id=>{pk}")
        msg=Message.objects.filter(Q(room__id=pk))
        if request.GET.get("search"):
            print(f'search={request.GET.get("search")}')
            message_id=request.GET.get("search")
            msg=Message.objects.filter(Q(id=message_id))

        
        # print(f"✅✅messag qs:{msg}")

        if not msg:
            return Response({
                "msg_lst":"empty room",
                "message":"error in posting msg"
            },status=status.HTTP_200_OK) 
        

        serializer=MessageSerializerForCreation(msg,many=True)

        if serializer.data:
            # print(f"✅✅Serializer{serializer.data}")
            return Response({
                "messages":serializer.data
            },status=status.HTTP_200_OK)

        return Response({
            "error":serializer.errors,
            "message":"error in posting msg"
        },status=status.HTTP_400_BAD_REQUEST) 
   
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


