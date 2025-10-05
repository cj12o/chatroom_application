from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.db.models import Q
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.decorators import api_view

# token = Token.objects.create(user=...)
# print(token.key)


from ..models.userprofile_model import UserProfile,User
from ..serializers.user_serializer import UserSerializer,AdminLoginSerializer,SignupSerializer
from ..serializers.userprof_serializer import UserProfSerializer
#for admin
class LoginApiview(APIView):
    
    def post(self,request):
        data=request.data
        serializer=AdminLoginSerializer(data=data) 
        if serializer.is_valid():
            user=User.objects.get(Q(email=data["email"]))
            userprofile=UserProfile.objects.filter(Q(user__email=data["email"]))
            serializer_2=UserProfSerializer(userprofile,many=True)
            token,created=Token.objects.get_or_create(user=user) 
            # print(f"{token}")

            if len(serializer_2.data)>0:
                print(f"✅✅Serializer:{serializer_2}")
                serializer_2.data[0]['profile_pic']=f"http://127.0.0.1:8000"+serializer_2.data[0]['profile_pic']
                return Response({
                    "userdata":serializer.data,
                    "profile":serializer_2.data,
                    "name":str(user.username),
                    "token":token.key,
                    "message":"Admin logged in "
                },status=status.HTTP_200_OK)
            else:
                return Response({
                "userdata":serializer.data,
                "profile":[],
                "name":str(user.username),
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

    def get(self,request):
        if request.user:
            request.user.auth_token.delete()
            return Response({
                "message":"logged out"
            },status=status.HTTP_200_OK)
        
        return Response({
            "message":"logout failed"
        },status=status.HTTP_400_BAD_REQUEST)



class SignUpApiview(APIView):
    def post(self,request):
        data=request.data
        serializer=SignupSerializer(data=data)
        if serializer.is_valid():
            # print(serializer.data)
            serializer.save()
            return Response({
                "userdata":serializer.data,
                "message":"user registered"
            },status=status.HTTP_200_OK)
                
        return Response({
            "errors":serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)


class UserApiview(APIView):
    permission_classes=[IsAdminUser]
    authentication_classes=[TokenAuthentication,BasicAuthentication]
    #get all users or login/?name=xxxx
    def get(self,request):
        
        print(f"{request.GET.get("name")}")
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