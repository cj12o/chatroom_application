from ..models.user_history_model import History
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from ..models.user_history_model import History
from datetime import datetime
from django.contrib.auth.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def setHistory(request):
    try:
    # data={'data': [{'id': 3, 'date': '9/10/2025, 8:05:03 pm'}, {'id': 4, 'date': '9/10/2025, 8:05:04 pm'}]}
        data=request.data
        rooms_visited=[]
        created_at=None
        user=User.objects.get(id=request.user.id)
        for obj in data["data"]:
            #order by date desc ->insert is used
            rooms_visited.insert(0,obj["id"])
            created_at=obj["date"]

        created_at=datetime.strptime(created_at, '%m/%d/%Y, %I:%M:%S %p')
        new_entry=History.objects.create(user=user,rooms_visited=rooms_visited,created_at=created_at)
        if new_entry:
            return Response({
                "message":"succesfully submitted history"
            },status=status.HTTP_200_OK)
        else:
            return Response({
                "message":"error  in submitting history"
            },status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"❌❌error:{str(e)}")
