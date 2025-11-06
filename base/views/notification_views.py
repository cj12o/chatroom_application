from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.db.models import Q
from rest_framework.decorators import api_view

from ..serializers.notification_serializer import NotificationSerializer

class NotificationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        try:
            user = request.user
            member_in_rooms=user.room_member.all()

            lst=[]
            for rm in member_in_rooms:
                
                # print(f"{len(rm.notification_set.all())}")
                serializer=NotificationSerializer(rm.notification_set.all(),many=True)
                
                if serializer:
                    lst.append(serializer.data)
                    
            return Response({
                "notifications":lst
            },status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "status":"BAD",
                "error":str(e)
            },status=status.HTTP_400_BAD_REQUEST)
