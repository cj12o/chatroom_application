from celery import shared_task
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from typing import TypedDict,Annotated,Literal
from langchain.messages import AnyMessage,SystemMessage,ToolMessage,HumanMessage
import operator
from langgraph.graph import StateGraph, START, END#,MessagesState
import json
from datetime import datetime
from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer
from django.conf import settings

llm=ChatOpenAI(
    base_url=settings.LLM_BASE_URL,
    model=settings.LLM_MODEL_NAME,
    api_key=settings.LLM_API_KEY
)

# ------------------------------------------AGENT------------------------------------------------



class MessagesState(TypedDict):
    messages:Annotated[list[AnyMessage],operator.add]
    llm_calls:int

class Context(TypedDict):
    room_name:str
    room_description:str
    #chats

context:Context={}

@tool(description="this tool generates interesting poll to increase chat room's activity")
def pollGenerator():
    
    """
    This tool generates interesting poll to increase chat room's activity.

    Args:
        state: agent's state
    """
    print("---------------POLL GEN CALLED---------------------------")
    SYSTEM_PROMPT=f""" 
    You are an expert poll generator generate a poll based on given room details:
    Chat Room Name:{context["room_name"]}
    Chat Room Description:{context["room_description"]}
    
    Output must be in this JSON format only:
    {{
        "question":"poll title ",
        "options":[choice 1,choice 2]
    }}

    """


    llm_output=llm.invoke([SystemMessage(content=SYSTEM_PROMPT)])
    # print(f"\n=====poll_gen output:{llm_output}=======\n")

    return llm_output.content



@tool(description="this tool generates interesting thread/comments to increase chat room's activity")
def threadGenerator():
    
    """
    This tool generates interesting threads/comments  to increase chat room's activity.

    Args:
        state: agent's state
    """
    print("---------------THREADGEN GEN CALLED---------------------------")
    SYSTEM_PROMPT=f""" 
    You are an expert in the room's topic  ,generate an interesting thread/comment based on given room details:
        Chat Room Name:{context["room_name"]}
        Chat Room Description:{context["room_description"]}
        
    Instructions:
    - Thread should be small and interesting (50-100) words maximum 
    - if you can give any url of website or article related to thread , it not mandatory but good to have 
    """


    llm_output=llm.invoke([SystemMessage(content=SYSTEM_PROMPT),HumanMessage(content="generate thread")])
    # print(f"\n=====poll_gen output:{llm_output}=======\n")
    
    return llm_output.content


tools=[pollGenerator,threadGenerator]
llm_with_tools=llm.bind_tools(tools)
tool_toolname_mapper={tool.name:tool for tool in tools}


def llm_node(state: dict) -> dict:
    """
    Node that decides whether to call tools or generate a direct response.
    The LLM acts as an engagement agent for a chat room.
    """

    SYSTEM_PROMPT = """ 
    You are an expert **Chat Room Engagement Agent**.
    Your goal is to **increase engagement and activity** in this room
    by making conversations more interesting, interactive, or fun.

    ## Instructions:
    - Always understand the current context from the conversation messages.
    - If interactivity can be increase by generating a  polll , call  the `pollGenerator` tool.
    - else call `threadGenerator` tool.
 

    ## Available tool:
    - pollGenerator(context: str) → Generates a poll for the room to increase engagement.
    - threadGenerator(context: str) → Generates a thread for the room to increase engagement.

    ## Guidelines:
    - Do not repeat user messages.
    - Be concise and engaging.
    - Always call the tool ,which makes the chat more interactive.
    - If you call a tool, provide only the tool call — no extra commentary.
    - calling a tool is manadatory
    
    """

    llm_output = llm_with_tools.invoke(
        [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    )

    return {
        "messages": [llm_output],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }



def tool_node(state:dict):
    
    """
    tool gets called.
    """

    print("Tool node called")
    outputs=[]
    for message in state["messages"][-1].tool_calls:
        tool_name=message["name"]
        print(f"TOOL CALLED:{tool_name}")
        llm_output=tool_toolname_mapper[tool_name].invoke(None)
        outputs.append(ToolMessage(content=llm_output,tool_call_id=message["id"]))
        break
        

    return {
        "messages":outputs,
        "llm_calls":state.get("llm_calls",0)+1
    }



def re_run(state: dict) -> Literal["tool_node",END]:
    """
    Decides whether to call a tool next or end the execution.
    """
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tool_node"
    return END

@shared_task
def main(room_id:int,room_name:str,room_description:str)->dict:

    graph=StateGraph(MessagesState)

    graph.add_node(llm_node)
    graph.add_node(tool_node)

    graph.add_edge(START,"llm_node")
    graph.add_conditional_edges("llm_node",re_run,[END,"tool_node"])
    graph.add_edge("tool_node",END)

    agent=graph.compile()
    context["room_description"]=room_description
    context["room_name"]=room_name
    # result=agent.invoke({"messages":[HumanMessage("make chat room interactive")],"llm_calls":0},{"recursion_limit": 10,"max_iteration":1})
    result=agent.invoke({"messages":[HumanMessage("make chat room interactive")],"llm_calls":0},recursion_limit=10,max_iteration=1)


    idx=0
    sol={}
    poll_gen_called_flag=False
    for x in result["messages"]:
        if hasattr(x,"content"):
            if len(x.content)>0 and hasattr(x,"tool_call_id"):

                if poll_gen_called_flag:
                    sol["content"]=json.loads(x.content)
                    
                else: 
                    sol["content"]=x.content
                
                
            if hasattr(x,"tool_calls"):
                tool_called=x.tool_calls[0]["name"]
                if tool_called=="pollGenerator":
                    poll_gen_called_flag=True
                # print(f"TOOL CALLED {x.tool_calls[0]["name"]}")
                sol["tool_called"]=tool_called
        
        idx=idx+1
    #roomid 
    sol["room_id"]=room_id
    print(f"🐐🐐SOL FROM AGENT:{sol}")
    return sol

# --------------------------------------------------Helper FUNC------------------------------------

@shared_task
def savePolltoDb(room_id:int,username:str,message:dict,parent:int=None):
    try:
        from base.models import Room,Message,Poll
        from django.contrib.auth.models import User 
        from base.logger import logger 
    
        room=Room.objects.get(id=room_id)
        author=User.objects.get(username=username)
        
        msg=Message.objects.create(room=room,author=author,message="")
        if parent is not None:
            parent_msg=Message.objects.get(id=parent)
            msg.parent=parent_msg

        msg.save()

        author=User.objects.get(username="Agent")
        room=Room.objects.get(id=room_id)

        new_poll=Poll.objects.create(message=msg,author=author,room=room,question=message["question"],choices={"choices":message["options"]})
        
        return (msg.id,new_poll.id)
    except Exception as e:
        logger.error(f"POLL NOT SAVED,error:{str(e)}")

@shared_task
def saveThreadToDb(room_id:int,username:str,message:str)->int:
    try:
        from base.models import Message,Room
        from django.contrib.auth.models import User
        from base.logger import logger 

        room=Room.objects.get(id=room_id)
        author=User.objects.get(username=username)

        
        msg=Message.objects.create(room=room,author=author,message=message)
        msg.save()
        return msg.id
    except Exception as e:
        logger.fatal(f"THREAD NOT SAVED,error:{str(e)}")

@shared_task
async def connectToWs(tool_called:str,message:str,message_id:int,room_id:int,parent=None):
    try:
        from base.logger import logger

        channel_layer=get_channel_layer()
        await channel_layer.group_send(
            f"room_{str(room_id)}",
            {
                "type":"chat_message",
                "tool_called":tool_called,
                "task":"chat",
                "message": message,  
                "parent":parent,
                "username":"Agent",
                "message_id":message_id,
                # "status": True
            }
        )
    except Exception  as e:
        logger.error(f"❌❌ERROR in connecting to ws(AGENT) :{str(e)}")


@shared_task
def start_agent():
    try:
        from base.models import Room,Message
        from django.db.models import Q
        from django.utils.dateparse import parse_datetime
        from base.logger import logger

        """
        1)call main to get result
        2)save in database 
        3)(in app)signal->ws

        """

        #TODO:ADD POLL CREATED ALSO 
        agent_msg=None
        rooms=Room.objects.all()

        day_diff=0
        hour_diff=0
    
        for r in rooms:
            
            lastMsg=Message.objects.filter(Q(room__id=r.id)).order_by('-created_at')[0]
            dt_created=parse_datetime(str(lastMsg.created_at))
            
            dt_now=datetime.now()

            if dt_now.day-dt_created.day>=day_diff:
                
                agent_msg=main(room_id=r.id,room_name=r.name,room_description=r.description)
                
            
            elif dt_now.hour-dt_created.hour>=hour_diff:
                agent_msg=main(room_id=r.id,room_name=r.name,room_description=r.description)
                
            
            if agent_msg is not None and "tool_called" in agent_msg:  
                if agent_msg["tool_called"]=="pollGenerator":
                    savePolltoDb.delay(room_id=agent_msg["room_id"],username="Agent",message=agent_msg["content"])

                else: 
                    message_id=saveThreadToDb(room_id=agent_msg["room_id"],username="Agent",message=agent_msg["content"])
                    # asyncio.run(connectToWs(tool_called="threadGenerator",message=agent_msg["content"],message_id=message_id,room_id=r.id))
                    async_to_sync(connectToWs)(tool_called="threadGenerator",message=agent_msg["content"],message_id=message_id,room_id=r.id)
    
    except Exception as e:
        logger.fatal(f"ERROR in starting agent: {str(e)}")
