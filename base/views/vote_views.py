from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from rest_framework.views import APIView

from ..models.message_model import Message,Vote

class voteApiview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def get(self,request,pk):
        message=Message.objects.first()
        votes=Vote.objects.filter(Q(user__username=request.user.username)& Q(room__id=pk))
        lst=[]
        for v in votes:
            dct={"message_id":v.message.id,"vote_type":v.vote}
            lst.append(dct)
            # print(f"Vote:{v.message.id} and {v.vote}")
        return Response({
            "votes":lst
        },status=status.HTTP_200_OK)