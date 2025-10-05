from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from rest_framework.views import APIView

from ..models.topic_model import Topic
from  ..serializers.topic_serializer import TopicSerializer

from ..views.topic_filter import topicsList

#for admin set topic(parent topic) but get every one 
class TopicApiview(APIView):
    permission_classes=[IsAdminUser]
    authentication_classes=[TokenAuthentication]

    def get_permissions(self):
        if self.request.method=="GET":
            # print(f"self.request.method:{self.request.method}")
            return []  
        elif self.request.method=="POST":
            # print(f"self.request.method:{self.request.method}")
            return [IsAdminUser()]  

    def get(self,request):
        topics=Topic.objects.all()
        serializer=TopicSerializer(topics,many=True)
        
        if serializer:
            # print(f"✅✅Serializer{serializer}")

            return Response({
                "topics":serializer.data
            },status=status.HTTP_200_OK)
        
        return Response({
            "errors":serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)
    
    def post(self,request):
        data=request.data
        serializer=TopicSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            # print(f"✅✅Serializer{serializer}")
            return Response({
                "topics":serializer.data,
                "message":"topic created"
            },status=status.HTTP_200_OK)
        
        return Response({
            "errors":serializer.errors,
            "message":"error in topic creation"
        },status=status.HTTP_400_BAD_REQUEST)
    

