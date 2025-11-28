from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.db.models import Q
from rest_framework.decorators import api_view,authentication_classes,permission_classes

from ..serializers.notification_serializer import PersonalNotificationSerializer

class NotificationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """gives notification for user """
        try:
            qs=request.user.personalnotification_user.filter(Q(mark_read=False))

            serializer=PersonalNotificationSerializer(qs,many=True)
                
            #     if len(serializer.data)>0:
            #         lst.append(serializer.data)
                    
            return Response({
                "notifications":serializer.data
            },status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "status":"BAD",
                "error":str(e)
            },status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getUnsendNotificationCnt(request):
    try:
        count=request.user.personalnotification_user.filter(mark_read=False).count()
        return Response({
            "count":count
        },status=status.HTTP_200_OK)
    except Exception as e: 
        pass