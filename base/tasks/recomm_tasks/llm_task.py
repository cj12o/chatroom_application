from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel,Field
from typing import List
import uuid
from django.conf import settings
from celery import shared_task

class RoomFormat(BaseModel):
    room_name:str=Field(description="room_name")
    room_id:int=Field(description="room_id")
    reason:str=Field(description="reason why this room is recommended")

class RespFormat(BaseModel):
    recommendation:List[RoomFormat]

llm=ChatOpenAI(
    base_url=settings.LLM_BASE_URL,
    model=settings.LLM_MODEL_NAME,
    api_key=settings.LLM_API_KEY,
    streaming=True,
)


llm_structured_op=llm.with_structured_output(RespFormat)

template = ChatPromptTemplate.from_messages([
    ("system", """
Role: You are a chatroom recommender.

Available rooms (List_of_rooms): {room_lst}
User history: {user_history_lst}
     

Rules:
1) Only pick rooms from List_of_rooms. Do NOT invent new rooms.
2) Give at least 4 recommendations.
3) Sort recommendations in decreasing order of importance.
4) Provide a short reason for each recommendation based on User history.
5) Refer to the user as "you" in explanations.
6)Do not recommend same rooms twice.     

""")
])


@shared_task
def Recommend(room_list:list,user_history:list): 
    """takes in user history,room_list prompts to llm and returns list of recommended rooms"""
    
    try:
        from base.views.logger import logger

        room_str="\n".join(f"room_description: \n {dct['document']}" for dct in room_list)
        user_hist_str="\n".join(f"room_id:{dct["id"]} room_name:{dct["name"]} room_description:{dct["description"]}" for dct in user_history)
        
        prompt = template.format_messages(
            room_lst=room_str,
            user_history_lst=user_hist_str
        )

        response=llm_structured_op.invoke(prompt)
        lst=[]
        for i in range(0,len(response.recommendation)):
            dct={}
            dct["name"]=response.recommendation[i].room_name
            dct["id"]=response.recommendation[i].room_id
            dct["reason"]=response.recommendation[i].reason
        
            lst.append(dct)
        
        return lst
    except Exception as e:
        logger.error(e)

@shared_task
def insertRecommInDB(recom_dct:dict,username:str):
    from base.models import Recommend,Room
    from django.contrib.auth.models import User
    from base.views.logger import logger

    user=User.objects.get(username=username)
    try:
        for dct in recom_dct:
            room=Room.objects.get(id=dct["id"])
            Recommend.objects.create(user=user,room=room,reason=dct["reason"],session=uuid.uuid4())
    except Exception as e:
        logger.error(e)

@shared_task 
def orchestrator(username:str,sessioncount:int,per_session_hist_count:int):
    """
    1)get user hist 
    2)get cosin sim rooms
    3)recommend(llm)
    4)insert in db
    
    """
    from .recommend_task import HistList,getCosinSimRooms
    from base.models import Room
    from .llm_task import insertRecommInDB
    from base.views.logger import logger
    try:
        user_history_dict=HistList(username=username,x=sessioncount,k=per_session_hist_count)
       
      
        resultant_list=getCosinSimRooms(user_history_dict=user_history_dict)
        room_list=[]
        for k,v in user_history_dict.items():
            for r_id,_  in v.items():
                room=Room.objects.get(id=r_id)
                room_list.append({"id":r_id,"name":room.name,"description":room.description})

        final_rooms_to_recommend=Recommend(room_list=resultant_list,user_history=room_list)
        
        insertRecommInDB.delay(final_rooms_to_recommend,username)
    except Exception as e:
        logger.error(e)
