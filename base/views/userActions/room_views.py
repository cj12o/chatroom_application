from rest_framework.decorators import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from models import Room

class RoomView(APIView):
    """
    return rooms ->admin +members
    """
    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def get(request,pk):
        try:
            user=request.user
            if pk==1:
                qs=user.author_rooms.all()
            
            

        except Exception as e:
            print(f"ERROR in adding member:{str(e)}")
            return Response({f"error in adding member {str(e)}"},status=status.HTTP_400_BAD_REQUEST)