from ..models.user_history_model import History
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from ..models.user_history_model import History
from datetime import datetime
from django.contrib.auth.models import User
from ..models import Room
from ..tasks.recomm_tasks.llm_task import orchestrator


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def setHistory(request):
    try:
    # data={'data': [{'id': 3, 'date': '9/10/2025, 8:05:03 pm'}, {'id': 4, 'date': '9/10/2025, 8:05:04 pm'}]}
       
        data=request.data
        print(f"✅✅data:{data}")
        rooms_visited_lst=[]
        session=data["data"]["sessionId"]
        print(f"✅✅sessioId:{session}")
        user=User.objects.get(id=request.user.id)

        room_data={}  #id:time_spent_total

        for obj in data["data"]["visited_rooms"]:
            #order by date desc ->insert is used
            room_id=obj["id"]
            time_spent_room=obj["timespent"]

            if room_id in rooms_visited_lst:
                room_data[room_id]=int(time_spent_room)+room_data[room_id]
            else:   
                rooms_visited_lst.append(room_id)
                room_data[room_id]=int(time_spent_room)
                

        # for k,v in room_data.items():
            # room=Room.objects.get(id=k)
        user=User.objects.get(id=request.user.id)
        History.objects.create(user=user,session=session,hist=room_data)

        orchestrator.delay(user.username,2,2)
        #TODO :call recomm

        return Response({
            "message":"succesfully submitted history"
        },status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌❌Error:{str(e)}")
        return Response({
            "message":"error in submitting history",
            "error":str(e)
        },status=status.HTTP_400_BAD_REQUEST) 


