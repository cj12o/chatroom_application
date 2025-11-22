from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from ..models import Room
from ..views.logger import logger
from django.db.models import Count,When,Case,Value,QuerySet,Q
from rest_framework.pagination import PageNumberPagination
from ..serializers.room_edit_serializer import Room_memeber_stats_seriaizer


class RoomStatsPagination(PageNumberPagination):
    page_size = 2

class RoomEditView(APIView):    
    # permission_classes=[IsAuthenticated]
    # authentication_classes=[TokenAuthentication]

    def get(self,request,pk):
        """gives 
            stats
        {
            "id": 0,
            "name": "ALEX_123",
            "msg_count": 4,
            "vote_count": 0
        },
        {
       
        """
        try:
            paginator=RoomStatsPagination()

            member_message_counts = (
                Room.objects.get(id=pk).members
                .annotate(msg_count=Count("author_message", filter=Q(author_message__room__id=pk)),
                          vote_count=Count("user_votes", filter=Q(user_votes__room__id=pk)))
            ).order_by("-msg_count", "-vote_count")  
                

            result_page=paginator.paginate_queryset(queryset=member_message_counts,request=request)
            serializer=Room_memeber_stats_seriaizer(result_page,many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            logger.error(e)
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
