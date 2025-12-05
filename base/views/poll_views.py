from ..models.poll_model import Poll,PollVote
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

from ..serializers.poll_serializer import PollSerializer,VoteSerializer
import json
class Voteview(APIView):
    # permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    
            
    def get(self,request,pk):
        """
        returns votes
        {
    "resp": {
        "19": {
            "0": 0,
            "1": 2,
            "user_has_vote": true,
            "user_vote": 2
        }
    }
}
        """
        try:
            polls=Poll.objects.filter(Q(room__id=pk))
            print(f"Cnt:{len(polls)}")
            dct_main={}
            for poll in polls: 
                choices=[idx for idx,_ in enumerate(poll.choices)]
                dct={}
                for ch in choices:
                    dct[ch]=PollVote.objects.filter(Q(poll__id=poll.id)&Q(choiceSelected=ch)).count()
                dct["user_has_vote"]=False
                dct["user_vote"]=-1
                if request.user.is_authenticated:
                    vote=PollVote.objects.filter(Q(poll__id=poll.id)&Q(user__id=request.user.id)).first()
                    if vote is not None:
                        dct["user_has_vote"]=True
                        dct["user_vote"]=vote.choiceSelected
                dct_main[poll.id]=dct
            return Response({
                "polls":dct_main
            },status=status.HTTP_200_OK)
            # else: raise Exception(serializer.error_messages)
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
            

    