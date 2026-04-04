from pydantic import BaseModel,Field
from typing import List
from django.conf import settings
from base.services.llm_services import get_model_with_structed_output
from base.services.prompt_services import get_prompt

class RoomFormat(BaseModel):
    room_name:str=Field(description="room_name")
    room_id:int=Field(description="room_id")
    reason:str=Field(description="reason why this room is recommended")

class RespFormat(BaseModel):
    recommendation:List[RoomFormat]




def Recommend(room_list:list,user_history:list): 
    
    room_str="\n".join(f"room_id:{dct.get('id')} room_name:{dct.get('name')} room_description:{dct.get('description')}" for dct in room_list)
    user_hist_str="\n".join(f"room_id:{dct.get('id')} room_name:{dct.get('name')} room_description:{dct.get('description')}" for dct in user_history)

    system_prompt=get_prompt("recommend.md")

    humanprompt=f"""
    Available rooms (List_of_rooms): {room_str}
    User history: {user_hist_str}
    """

    llm=get_model_with_structed_output(settings.OPENAI_MODEL_RECOMMENDATION,RespFormat)
    response=llm.invoke([system_prompt,humanprompt])

    print(f"✅✅LLm response:{response}")

    lst=[]
    for i in range(0,len(response.recommendation)):
        dct={}
        dct["name"]=response.recommendation[i].room_name
        dct["id"]=response.recommendation[i].room_id
        dct["reason"]=response.recommendation[i].reason
        print(f"✅✅LLm response:{response.recommendation[0].room_name}")
        lst.append(dct)
    print(lst)
    return lst
    

