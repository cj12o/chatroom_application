from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from ..serializers.notification_serializer import PersonalNotificationSerializer
from ..services.notification_service import get_unread_notifications, mark_notifications_read, get_unread_count
from ..threadPool import ThreadPoolManager


class NotificationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """gives notification for user"""
        try:
            qs = get_unread_notifications(request.user)
            ids = [notification.id for notification in qs]
            serializer = PersonalNotificationSerializer(qs, many=True)

            # mark as read in background so response isn't delayed
            ThreadPoolManager.get().submit(lambda: mark_notifications_read(ids))

            return Response({
                "notifications": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "BAD",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getUnsendNotificationCnt(request):
    try:
        count = get_unread_count(request.user)
        return Response({"count": count}, status=status.HTTP_200_OK)
    except Exception:
        pass
