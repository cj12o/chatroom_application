from ..models.poll_model import Poll, PollVote
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
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

    def post(self, request, pk):
        """Submit or update a poll vote. pk = poll_id"""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            choice = request.data.get("choice")
            if choice is None:
                return Response({"error": "choice is required"}, status=status.HTTP_400_BAD_REQUEST)
            poll = Poll.objects.get(id=pk)
            PollVote.objects.update_or_create(
                poll=poll, user=request.user,
                defaults={"choiceSelected": int(choice)}
            )
            return Response({"status": "ok"}, status=status.HTTP_200_OK)
        except Poll.DoesNotExist:
            return Response({"error": "Poll not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

    
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
            

    