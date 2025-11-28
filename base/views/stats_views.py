from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count,When,Case,Value,QuerySet,Q
from ..logger import logger
from ..models import Room,UserProfile,Message
from django.utils.timezone import now

@api_view(['GET'])
def getStats(request):
    "return stats for dashboard"
    try:
        rm_cnt=Room.objects.count()
        user_cnt=UserProfile.objects.aggregate(
            online_cnt=Count("id",filter=Q(is_online=True)),
            total_user_cnt=Count("id")
        )
        
        msg_today_cnt=Message.objects.filter(Q(created_at__date=now().date())).count()

        return Response({
            "room_count":rm_cnt,
            "online_users_count":user_cnt["online_cnt"],
            "message_count":msg_today_cnt,  
            "total_users_count":user_cnt["total_user_cnt"]
        },status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)