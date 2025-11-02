from langchain_openai import ChatOpenAI
from langchain.tools import tool
from typing import TypedDict,Annotated,Literal
from langchain.messages import AnyMessage,SystemMessage,ToolMessage,HumanMessage
import operator
from langgraph.graph import StateGraph, MessagesState, START, END
import json

import os

from dotenv import load_dotenv

load_dotenv()

llm=ChatOpenAI(
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM"),
    api_key=os.getenv("LLM_API_KEY")
)



class MessagesState(TypedDict):
    messages:Annotated[list[AnyMessage],operator.add]
    llm_calls:int

class Context(TypedDict):
    room_name:str
    room_description:str
    #chats


@tool(description="this tool generates interesting poll to increase chat room's activity")
def pollGenerator():
    
    """
    This tool generates interesting poll to increase chat room's activity.

    Args:
        state: agent's state
    """
    print(f"---------------POLL GEN CALLED---------------------------")
    SYSTEM_PROMPT=f""" 
    You are an expert poll generator generate a poll based on given room details:
    Chat Room Name:{"Python room"}
    Chat Room Description:{"Discuss regarding highly interesting updates and features for python ecosystem."}
    
    Output must be in this JSON format only:
    {{
        "question":"poll title ",
        "options":[choice 1,choice 2]
    }}

    """


    llm_output=llm.invoke([SystemMessage(content=SYSTEM_PROMPT)])
    print(f"\n=====poll_gen output:{llm_output}=======\n")

    return llm_output.content



@tool(description="this tool generates interesting thread/comments to increase chat room's activity")
def threadGenerator():
    
    """
    This tool generates interesting threads/comments  to increase chat room's activity.

    Args:
        state: agent's state
    """
    print(f"---------------THREADGEN GEN CALLED---------------------------")
    SYSTEM_PROMPT=f""" 
    You are an expert in the room's topic  generate an interesting thread/comment based on given room details:
    Chat Room Name:{"Python room"}
    Chat Room Description:{"Discuss regarding highly interesting updates and features for python ecosystem."}
    """


    llm_output=llm.invoke([SystemMessage(content=SYSTEM_PROMPT),HumanMessage(content="generate thread")])
    print(f"\n=====poll_gen output:{llm_output}=======\n")
    
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
    - always call the `pollGenerator` tool.
 

    ## Available tool:
    - pollGenerator(context: str) → Generates a poll for the room to increase engagement.
    - threadGenerator(context: str) → Generates a thread for the room to increase engagement.

    ## Guidelines:
    - Do not repeat user messages.
    - Be concise and engaging.
    - Only call the tool if it makes the chat more interactive.
    - If you call a tool, provide only the tool call — no extra commentary.

    
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

    print(f"Tool node called")
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



def re_run(state: dict) -> Literal["tool_node", END]:
    """
    Decides whether to call a tool next or end the execution.
    """
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tool_node"
    return END


def main():
    

    graph=StateGraph(MessagesState)

    graph.add_node(llm_node)
    graph.add_node(tool_node)

    graph.add_edge(START,"llm_node")
    graph.add_conditional_edges("llm_node",re_run,[END,"tool_node"])
    graph.add_edge("tool_node",END)

    agent=graph.compile()


    result=agent.invoke({"messages":[HumanMessage("make chat room interactive")],"llm_calls":0},{"recursion_limit": 10})


    # for m in result["messages"]:
    #     print(m)

    # result["llm_calls"]
    idx=0
    sol={}
    for m in result["messages"]:
        if hasattr(m,"content") and len(m.content)>1 and idx==len(result["messages"])-1:    

            # sol["message"]=m.content
            sol["message"]=json.loads(m.content)
            

        if hasattr(m,"tool_calls"):
            print(f"tool called:{m.tool_calls}")

            sol["tool_called"]=m.tool_calls[0]["name"]
        

        idx=idx+1
    #roomid 
    sol["room_id"]=1    
    print(f"🐐🐐SOL FROM AGENT:{sol}")
    return sol

