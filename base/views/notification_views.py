from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.db.models import Q
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from  ..logger import logger
from ..serializers.notification_serializer import PersonalNotificationSerializer
from ..models import PersonalNotification
from ..threadPool import ThreadPoolManager
def mark_read(ids:list):
    try:
        PersonalNotification.objects.filter(id__in=ids).update(mark_read=True)
    except Exception as e:
        logger.error(e)

class NotificationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """gives notification for user """
        "as rest based so if notification page gets opened then all notifications will be marked as read"
        try:
            qs=request.user.personalnotification_user.filter(Q(mark_read=False))
            
            ids=[notification.id for notification in qs]
            serializer=PersonalNotificationSerializer(qs,many=True)
            
            #marking all notifications as read,delayed becuase hand to hand update make notification ->[]
            ThreadPoolManager.get().submit(lambda:mark_read(ids))
            
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