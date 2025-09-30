from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from ..models.user_model import UserProfile,User
from ..serializers.user_serializer import UserSerializer

class UserApiview(APIView):
    def get(self,request):
        try:
            qs=User.objects.all()
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
        except Exception as e:
            return Response({
                "Exception":str(e)
            })
        
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