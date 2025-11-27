from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.db.models import Q
from rest_framework.decorators import api_view

from ..serializers.notification_serializer import PersonalNotificationSerializer

class NotificationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """gives notification for user """
        try:
            request.user.personalnotification_user.all()

            # serializer=PersonalNotificationSerializer(rm.notification_set.filter(sent_status=False),many=True)
                
            #     if len(serializer.data)>0:
            #         lst.append(serializer.data)
                    
            return Response({
                "notifications":""
            },status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "status":"BAD",
                "error":str(e)
            },status=status.HTTP_400_BAD_REQUEST)
