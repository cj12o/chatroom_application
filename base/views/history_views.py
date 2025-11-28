from ..models.user_history_model import History
from ..models.user_history_model import History
from datetime import datetime
from django.contrib.auth.models import User
from ..models import Room
from ..tasks.recomm_tasks.llm_task import orchestrator
from ..logger import logger



def setHistory(data:dict,user:object):
    try:
    # data={'data': [{'id': 3, 'date': '9/10/2025, 8:05:03 pm'}, {'id': 4, 'date': '9/10/2025, 8:05:04 pm'}]}
       
        rooms_visited_lst=[]
        session=data["sessionId"]
        

        room_data={}  #id:time_spent_total

        for obj in data["visited_rooms"]["current"]:
            #order by date desc ->insert is used
            room_id=obj["id"]
            time_spent_room=obj["timespent"]

            if room_id in rooms_visited_lst:
                room_data[room_id]=int(time_spent_room)+room_data[room_id]
            else:   
                rooms_visited_lst.append(room_id)
                room_data[room_id]=int(time_spent_room)
                
    
        if(len(room_data.keys())<1): return
        
        History.objects.create(user=user,session=session,hist=room_data)

        orchestrator.delay(user.username,2,2)
        #TODO :call recomm
        
    except Exception as e:
        logger.error(e)
        return

