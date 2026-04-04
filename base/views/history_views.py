from ..models.user_history_model import History
from ..tasks.recomm_tasks.llm_task import orchestrator
from ..logger import logger



def setHistory(data:dict,user:object):
    try:
    # data={'data': [{'id': 3, 'date': '9/10/2025, 8:05:03 pm'}, {'id': 4, 'date': '9/10/2025, 8:05:04 pm'}]}
        print(data)
        session=data["sessionId"]
    

        room_data={}  #id:time_spent_total

        for obj in data["visited_rooms"]:
            #order by date desc ->insert is used
            room_id=int(obj["id"])
            time_spent_room=int(obj["timespent"])

            if room_id in room_data:
                room_data[room_id]=int(time_spent_room)+room_data[room_id]
            else:   
                room_data[room_id]=int(time_spent_room)
                
    
        if not room_data:
            return
        
        History.objects.create(user=user,session=session,hist=room_data)

        orchestrator.delay(user.username,2,2)
        print(f"✅✅Saved history")
        #TODO :call recomm
        
    except Exception as e:
        print(f"❌❌Error in setHistory:{str(e)}")
        logger.error(e)
        return

