from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

from ..models.message_model import Message
from ..serializers.reaction_serializer import ReactionSerializer


class ReactionApiview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def post(self,request,pk,q):
        print
        data=request.data
        user=User.objects.get(id=request.user.id)
        message=Message.objects.get(Q(id=pk) & Q(room__id=q))
        context={
            "msg":message,
            "user":user,
        }
        serializer=ReactionSerializer(data=data,context=context)
        if serializer.is_valid():
            # print(serializer.data)
            serializer.save()
            return Response({
                "reaction":serializer.data,
                "message":"Reaction posted"
            },status=status.HTTP_200_OK)
        return Response({
            "errors":serializer.errors,
            "message":"error in posting Reaction"
        },status=status.HTTP_400_BAD_REQUEST)
