from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.db.models import Q
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
# token = Token.objects.create(user=...)
# print(token.key)


from ..models.user_model import UserProfile,User
from ..serializers.user_serializer import UserSerializer,AdminLoginSerializer

#for admin
class LoginApiview(APIView):
    
    def post(self,request):
        data=request.data
        serializer=AdminLoginSerializer(data=data) 
        if serializer.is_valid():
            user=User.objects.get(Q(username=data["username"]))
            token,created=Token.objects.get_or_create(user=user) 
            # print(f"{token}")
            return Response({
                "userdata":serializer.data,
                "token":token.key,
                "message":"Admin logged in "
            },status=status.HTTP_200_OK)
    
        else:
            return Response({
                "errors":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)

    

class LogoutApiview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def post(self,request):
        serializer=AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            request.user.auth_token.delete()
            return Response({
                "message":"logged out"
            },status=status.HTTP_200_OK)
        
        return Response({
            "message":"logout failed",
            "errors":serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)





class UserApiview(APIView):
    permission_classes=[IsAdminUser]
    authentication_classes=[TokenAuthentication,BasicAuthentication]
    #get all users or login/?name=xxxx
    def get(self,request):
        
        print(f"{request.GET.get("name")}")
        print("ok")
        qs=User.objects.all()

        if request.GET.get("name"):
            name=request.GET.get("name")
            qs=qs.filter(username=name)
            if not qs:
                return Response({
                    "errors":"Invalid user"
                },status=status.HTTP_400_BAD_REQUEST)


        print(f"Qs=>{qs}")
        serializer=UserSerializer(qs,many=True)
        print(f"✅✅✅Serializer data={serializer.data}")
        if serializer.data:
            return Response({
                "userdata":serializer.data
            },status=status.HTTP_200_OK)
        
        else:
            return Response({
                "errors":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):
        userdata=request.data
        serializer=UserSerializer(data=userdata)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "userdata":serializer.data,
                "message":"user registered"
            },status=status.HTTP_200_OK)
        
        return Response({
            "errors":serializer.errors,
            "message":"error in user registration"
        },status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request):
        try:
            data=request.data
            user=User.objects.get(id=data["id"])
            
            if not user:
                return Response({
                    "errors":"Invalid user"
                },status=status.HTTP_400_BAD_REQUEST)

            print(f"✅✅User=>{user}")

            serializer=UserSerializer(instance=user,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "userdata":serializer.data,
                    "message":f"user updated"
                },status=status.HTTP_200_OK)
            
            return Response({
                "errors":serializer.errors,
                "message":f"error in user  updation"
            },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "Error":str(e)
            })
    
    def put(self,request):
        data=request.data
        user=User.objects.get(id=data["id"])
        if user:
            serializer=UserSerializer(instance=user,data=data,partial=False)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "userdata":serializer.data,
                    "message":f"user: updated"
                },status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "errors":serializer.errors,
                "message":f"error in user updation"
            },status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "errors":"Invalid id,no such user",
            "message":f"error in user  updation"
        },status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        user_id=request.data["id"]
        user=User.objects.get(id=user_id)
        
        if user:
            user.delete()
            return Response({
                "message":f" user deleted"
            },status=status.HTTP_200_OK)
        
        return Response({
            "errors":"Invalid id,no such user",
            "message":f"error in user  updation"
        },status=status.HTTP_400_BAD_REQUEST)