from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.db.models import Q
from rest_framework.authentication import BasicAuthentication,TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.conf import settings



from ..models.userprofile_model import User
from ..serializers.user_serializer import UserSerializer,AdminLoginSerializer,SignupSerializer


from ..threadPool import ThreadPoolManager
from ..views.history_views import setHistory

#for admin
class LoginApiview(APIView):
    
    def post(self,request):
        data=request.data
        serializer=AdminLoginSerializer(data=data) 
        if serializer.is_valid():
            user=User.objects.get(Q(email=data["email"]))
            token,created=Token.objects.get_or_create(user=user) 
            
            profile_pic=None
            if user.profile.profile_pic:
                profile_pic=f"{settings.SITE_BASE_URL}{user.profile.profile_pic.url}"
            
            return Response({
            "userdata":serializer.data,
            "name":str(user.username),
            "token":token.key,
            "profile_pic":profile_pic,
            "id":user.id,
            "message":"User logged in "
            },status=status.HTTP_200_OK)
        else:
            return Response({
                "errors":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)

    

class LogoutApiview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def post(self,request):
        try:
            
            if request.user.is_authenticated:
                data=request.data
                executor=ThreadPoolManager.get()
                executor.submit(setHistory,data,request.user)

                request.user.auth_token.delete()    
                
                return Response({
                    "message":"logged out"
                },status=status.HTTP_200_OK)


            else: 
                raise Exception("Invalid user")

        except Exception as e:
            print(f"Error in logout:{str(e)}")
            return Response({
                "Error":str(e)
            },status=status.HTTP_400_BAD_REQUEST)

class SignUpApiview(APIView):
    def post(self,request):
        data=request.data
        serializer=SignupSerializer(data=data)
        if serializer.is_valid():
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
                    "message":"user updated"
                },status=status.HTTP_200_OK)
            
            return Response({
                "errors":serializer.errors,
                "message":"error in user  updation"
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
                    "message":"user: updated"
                },status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "errors":serializer.errors,
                "message":"error in user updation"
            },status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "errors":"Invalid id,no such user",
            "message":"error in user  updation"
        },status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        user_id=request.data["id"]
        user=User.objects.get(id=user_id)
        
        if user:
            user.delete()
            return Response({
                "message":" user deleted"
            },status=status.HTTP_200_OK)
        
        return Response({
            "errors":"Invalid id,no such user",
            "message":"error in user  updation"
        },status=status.HTTP_400_BAD_REQUEST)