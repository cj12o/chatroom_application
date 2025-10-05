from rest_framework.views import APIView
from  rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from ..serializers.userprof_serializer import UserProfSerializer
from django.db.models import Q
from ..models.userprofile_model import UserProfile


class UserProfileApiview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    #get all users pk is username
    def get(self,request):
        user=User.objects.filter(id=request.user.id)
        # print(f"✅✅user=>{user}")
        if not user:
            return Response({
                "message":"Invalid user"
            })
        userprofile=UserProfile.objects.filter(Q(user__username=request.user.username)&Q(user__email=request.user.email))
        serializer=UserProfSerializer(userprofile,many=True,context={'request':request})
        if serializer:
            return Response({
                "userdata":serializer.data,
                "name":str(request.user.username)
            },status=status.HTTP_200_OK)
        
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