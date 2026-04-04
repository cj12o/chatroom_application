from ..models.poll_model import Poll
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

from ..serializers.poll_serializer import PollSerializer
from ..services.vote_service import get_poll_vote_summary


class Voteview(APIView):
    authentication_classes=[TokenAuthentication]

    def get(self,request,pk):
        """returns poll vote counts + user's vote for all polls in a room"""
        try:
            result = get_poll_vote_summary(pk, user=request.user)
            return Response({"polls": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

    
class Pollview(APIView):

    def get(self,request,pk):

        """
        pk: message_id
        returns all polls in a room
        """
        try:
            polls=Poll.objects.filter(Q(message__id=pk))
            serializer=PollSerializer(polls,many=True)

            return Response({
                "poll":serializer.data
            },status=status.HTTP_200_OK)
    
        except Exception as e:

            return Response({
                "status":str(e)
            },status=status.HTTP_400_BAD_REQUEST)
            

    