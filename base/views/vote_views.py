from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView

from ..services.vote_service import get_user_votes_for_room


class voteApiview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def get(self,request,pk):
        votes = get_user_votes_for_room(request.user.id, pk)
        return Response({"votes": votes}, status=status.HTTP_200_OK)
