from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel,Field
from typing import List
import logging
import time
import uuid

class RoomFormat(BaseModel):
    room_name:str=Field(description="room_name")
    room_id:int=Field(description="room_id")
    reason:str=Field(description="reason why this room is recommended")

from celery import shared_task

class RespFormat(BaseModel):
    recommendation:List[RoomFormat]

llm=ChatOpenAI(
    base_url="http://127.0.0.1:1239/v1/",
    model="hermes-3-llama-3.2-3b",
    api_key="lm_studio",
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


""")
])


@shared_task
def Recommend(room_list:list,user_history:list): 
    print(f"✅✅Room list:{room_list}")
    print(f"✅✅user  hist:{user_history}")

    # room_str="\n".join(f"room_id:{dct["id"]} room_name:{dct["name"]} room_description:{dct["document"]}" for dct in room_list)
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
        # print(f"✅✅LLm response:{response.recommendation[0].room_name}")
        lst.append(dct)
    # print(lst)
    return lst

@shared_task
def insertRecommInDB(recom_dct:dict,username:str):
    from base.models import Recommend,Room
    from django.contrib.auth.models import User

    user=User.objects.get(username=username)
    try:
        for dct in recom_dct:
            room=Room.objects.get(id=dct["id"])
            Recommend.objects.create(user=user,room=room,reason=dct["reason"],session=uuid.uuid4())
    except Exception as e:
        logging.fatal(e)

@shared_task 
def orchestrator(username:str,sessioncount:int,per_session_hist_count:int):
    """
    1)get user hist 
    
    """
    from .recommend_task import HistList,getCosinSimRooms
    from base.models import Room
    from .llm_task import insertRecommInDB
    try:
        user_history_dict=HistList(username=username,x=sessioncount,k=per_session_hist_count)
       
        # print(f"🤖🤖user history:{user_history_dict}")
        resultant_list=getCosinSimRooms(user_history_dict=user_history_dict)
        room_list=[]
        for k,v in user_history_dict.items():
            for r_id,_  in v.items():
                room=Room.objects.get(id=r_id)
                room_list.append({"id":r_id,"name":room.name,"description":room.description})


        # print(f"🤖🤖room list:{room_list}")
        final_rooms_to_recommend=Recommend(room_list=resultant_list,user_history=room_list)
        
        insertRecommInDB.delay(final_rooms_to_recommend,username)
        # print(f"🤖🤖resultant recom:{final_rooms_to_recommend}")
        # print(f"Result:{resultant_list}")
    except Exception as e:
        logging.fatal(f"Error in orchestrator {str(e)} ")
