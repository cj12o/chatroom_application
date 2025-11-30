from rest_framework import status
from rest_framework.response import Response    
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from ...models import Room


class MemeberApiView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def patch(self,request,pk):
        try:
            """add memeber to a room for authenticated user"""
            room_id=pk
            print(f"ROOM ID:{pk}")
            obj=Room.objects.get(id=room_id)
            obj.members.add(request.user)
            return Response({"added member"},status=status.HTTP_200_OK)
        except Exception as e:
            print(f"ERROR in adding member:{str(e)}")
            return Response({f"error in adding member {str(e)}"},status=status.HTTP_400_BAD_REQUEST)



    def delete(self,request,pk):
        try:
            """delete memeber to a room for authenticated user"""

            room_id=pk
            obj=Room.objects.get(id=room_id)
            obj.members.remove(request.user)
            return Response({"deleted member"},status=status.HTTP_200_OK)
        except Exception as e:
            print(f"ERROR in deleting member:{str(e)}")
            return Response({f"error in deleting member {str(e)}"},status=status.HTTP_400_BAD_REQUEST)



        