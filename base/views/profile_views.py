from rest_framework.views import APIView
from  rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from ..serializers.userprof_serializer import UserProfSerializer,RoomsCreatedSerializer
from ..serializers.room_serializer import RoomSerializer
from ..models.userprofile_model import UserProfile
from ..models.room_model import Room

class UserProfileApiview(APIView):

    """get user profile pk is userid"""

    # def get_permissions(self):
    #     if self.request.method=="GET":
    #         return []
    #     else: return [IsAuthenticated()]

    def get(self,request,q):
        user=User.objects.get(username=q)
        # print(f"✅✅user=>{user}")
        if not user:
            return Response({
                "message":"Invalid user"
            })
        print(f"✅✅USER:{user}")
        userprofile=UserProfile.objects.filter(Q(user__username=q))
        serializer=UserProfSerializer(userprofile,many=True,context={'request':request})
        if serializer:
            #####
            rooms=Room.objects.filter(Q(author__username=q))
            serializer_room=RoomsCreatedSerializer(rooms,many=True)

            ###member
            member_room=user.room_member.all()
            # print(f"✅✅memeber of rooms:{member_room}")
            

            member_room_lst=[]
            if member_room:
                for room in member_room:
                    dct={}
                    dct["name"]=room.name
                    dct["id"]=room.id
                    member_room_lst.append(dct)
                    # print(f"😀😀room:{room.name}")


            resp={"userdata":serializer.data,
                    "name":str(user.username),
                    "rooms_member":member_room_lst,
                    "email":user.email
                 }
            ##
            if serializer_room :
                lst=[]
                for room in serializer_room.data:
                    dct={}
                    dct["name"]=room["name"]
                    dct["id"]=room["id"]
                    lst.append(dct)
                resp["rooms_created"]=lst
            else:
                resp["rooms_created"]=[]
            
            
            
            return Response(resp,status=status.HTTP_200_OK)
            
        else:
            return Response({
                "errors":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):
        data=request.data
        serializer=UserProfSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message":"Initialized profile"
            },status=status.HTTP_201_CREATED)

        return Response({
            "errors":serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)

    # def patch(self,request):
    #     try:
    #         data=request.data
    #         user=User.objects.get(id=data["id"])
            
    #         if not user:
    #             return Response({
    #                 "errors":"Invalid user"
    #             },status=status.HTTP_400_BAD_REQUEST)

    #         print(f"✅✅User=>{user}")

    #         serializer=UserProfSerializer(instance=user,data=data,partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response({
    #                 "userdata":serializer.data,
    #                 "message":f"user updated"
    #             },status=status.HTTP_200_OK)
            
    #         return Response({
    #             "errors":serializer.errors,
    #             "message":f"error in user  updation"
    #         },status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({
    #             "Error":str(e)
    #         })
    #
    # def put(self,request):
    #     data=request.data
    #     user=User.objects.get(id=data["id"])
    #     if user:
    #         serializer=UserProfSerializer(instance=user,data=data,partial=False)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response({
    #                 "userdata":serializer.data,
    #                 "message":f"user: updated"
    #             },status=status.HTTP_400_BAD_REQUEST)

    #         return Response({
    #             "errors":serializer.errors,
    #             "message":f"error in user updation"
    #         },status=status.HTTP_400_BAD_REQUEST)
        
    #     return Response({
    #         "errors":"Invalid id,no such user",
    #         "message":f"error in user  updation"
    #     },status=status.HTTP_400_BAD_REQUEST)
    
    # def delete(self,request):
    #     user_id=request.data["id"]
    #     user=User.objects.get(id=user_id)
        
    #     if user:
    #         user.delete()
    #         return Response({
    #             "message":f" user deleted"
    #         },status=status.HTTP_200_OK)
        
    #     return Response({
    #         "errors":"Invalid id,no such user",
    #         "message":f"error in user  updation"
    #     },status=status.HTTP_400_BAD_REQUEST)