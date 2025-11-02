from ..models.poll_model import Poll,PollVote
from rest_framework.views import APIView
from ..models.message_model import Message
from rest_framework.decorators import permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

from ..serializers.poll_serializer import PollSerializer

class Voteview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def get(self,request,pk):
        """
        returns all votes of user
        """
        try:
            polls=Poll.objects.filter(Q(room__id=pk))
            for poll in polls:
                votes=PollVote.objects.filter(Q(user__id=request.user.id) & Q(poll__id=poll.id)) 
                for v in  votes:
                    print(f"✅✅votes:{v.choiceSelected}")
                return Response({
                    "votes":{v.poll.id:v.choiceSelected for v in votes}
                },status=status.HTTP_200_OK)
        
        except Exception as e:

            return Response({
                "status":str(e)
            },status=status.HTTP_400_BAD_REQUEST)
            

    
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
            

    