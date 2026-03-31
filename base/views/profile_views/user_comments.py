from rest_framework.views import APIView
from django.contrib.auth.models import User 
from  rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

class CommentsApiView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    def get(self,request,q):
        user=User.objects.get(username=q)
        if not user:
            return Response({
                "message":"Invalid user"
            })
        
    