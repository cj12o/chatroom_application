from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel,Field
from typing import List

class RoomFormat(BaseModel):
    room_name:str=Field(description="room_name")
    room_id:int=Field(description="room_id")
    reason:str=Field(description="reason why this room is recommended")

class RespFormat(BaseModel):
    recommendation:List[RoomFormat]

llm=ChatOpenAI(
    base_url="http://127.0.0.1:1239/v1/",
    model="hermes-3-llama-3.2-3b",
    api_key="lm_studio",
    streaming=True,
)
dewde

# llm_structured_op=llm.with_structured_output(RespFormat)

# template = ChatPromptTemplate.from_messages([
#     ("system", """
# Role: You are a chatroom recommender.

# Available rooms (List_of_rooms): {room_lst}
# User history: {user_history_lst}
     

# Rules:
# 1) Only pick rooms from List_of_rooms. Do NOT invent new rooms.
# 2) Give at least 4 recommendations.
# 3) Sort recommendations in decreasing order of importance.
# 4) Provide a short reason for each recommendation based on User history.
# 5) Refer to the user as "you" in explanations.


# """)
# ])



# def Recommend(room_list:list,user_history:list): 
#     # print(f"Room list:{room_list}")
#     # print(f"user  hist:{user_history}")

#     room_str="\n".join(f"room_id:{dct["id"]} room_name:{dct["name"]} room_description:{dct["description"]}" for dct in room_list)
#     user_hist_str="\n".join(f"room_id:{dct["id"]} room_name:{dct["name"]} room_description:{dct["description"]}" for dct in room_list)
    
#     prompt = template.format_messages(
#         room_lst=room_str,
#         user_history_lst=user_hist_str
#     )

#     response=llm_structured_op.invoke(prompt)
#     lst=[]
#     for i in range(0,len(response.recommendation)):
#         dct={}
#         dct["name"]=response.recommendation[i].room_name
#         dct["id"]=response.recommendation[i].room_id
#         dct["reason"]=response.recommendation[i].reason
#         # print(f"✅✅LLm response:{response.recommendation[0].room_name}")
#         lst.append(dct)
#     # print(lst)
#     return lst
    

