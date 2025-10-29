from langchain_classic.agents import AgentExecutor,create_react_agent,Tool,create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from pydantic import BaseModel,Field
from typing import Dict,List
from langchain_core.output_parsers import PydanticOutputParser
import json
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate


from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed
import time
import json
from pydantic import BaseModel,Field
from typing import List,Dict
from ..message_views import MessageApiview

from .testSocket import connectTows
import asyncio


llm=ChatOpenAI(
    # model="mistralai/mistral-nemo-instruct-2407",
    # model="qwen/qwen3-4b-thinking-2507",
    model="hermes-3-llama-3.2-3b",
    base_url="http://127.0.0.1:1239/v1/",
    api_key="dewfe",
)



class parser(BaseModel):
    content:dict=Field(description="response of llm")


class parser_tool2(BaseModel):
    content:str=Field(description="response of llm")
    
oup_parser=PydanticOutputParser(pydantic_object=parser)
oup_parser2=PydanticOutputParser(pydantic_object=parser_tool2)




# th_pl_exec=ThreadPoolExecutor(max_workers=3)

@tool
def pollGenerator(context: str) -> dict:
    """This tool generates a poll for the room to increase engagement.
    Returns: dictionary 
    """
    from .agent_view import executor as executor_thread_pool
    template=ChatPromptTemplate.from_messages([
        ("system",
        """
        you are a poll generator 
        based on context:{context} generate poll

        output in format:{format}
        """)   
    ])    

    llm_struct=llm.with_structured_output(parser)
    chain=template|llm_struct
    result=chain.invoke({"context":context,"format":oup_parser.get_format_instructions()}).content
    print(f"Result:{result}")


    executor_thread_pool.submit(lambda : asyncio.run(connectTows()))
    #trigger tkinter   
    #######

    return result


@tool
def generateThread(context:str)->str:
    """This tool generates a thread/comment and invite users for dicussions to increase engagement
    
    Returns: str 
    """
    from .agent_view import executor as executor_thread_pool
    template=ChatPromptTemplate.from_messages(
        [
            ("system",
             """
            based  on context:{context}

            generate an engaging thread and invite user thoughts    

            output in format:{format}
            """)
        ]
    )

    chain=template|llm.with_structured_output(parser_tool2)
    result=chain.invoke({"context":context,"format":oup_parser2.get_format_instructions()}).content
    
    print(f"Response from tool threadgen:{result}")
    

    executor_thread_pool.submit(lambda :asyncio.run(connectTows()))
    return result

    

def create_room_agent():
    tools = [pollGenerator,generateThread]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert assistant that makes chat rooms more interactive and viral."),
        ("human", 
        """Room Name: {room_name}
        Room Description: {room_desc}
        Recent Chats: {chats}


        task to complete:{input}
        Reasoning:{agent_scratchpad}
         
        based on provided tools call the correct one to complete task:
        pass context given as it is  to tools
        {tool_names}
        
        """)
    ])

    # ✅ Correct agent constructor
    agent = create_tool_calling_agent(llm, tools, prompt)

    # ✅ Executor to run agent
    executor = AgentExecutor(agent=agent, tools=tools,max_iterations=1,verbose=True,early_stopping_method= 'force')
    return executor


def main():
    
    print(f"✅✅Agent called")
    agent_executor = create_room_agent()
    
    room_data = {
        "room_name": "Python Developers Hub",
        "room_desc": "A community for Python enthusiasts to share code and learn",
        "chats": "User1: Anyone know good Python resources?\nUser2: I'm working on a Django project",
        "input": "Increase engagement in the room",
        "tool_names":["pollGenerator","generateThread"]
    }

    result = agent_executor.invoke(room_data)
    print("\n✅ AGENT RESULT:", result)


if __name__ == "__main__":

    time_start=time.time()
    main()
    print(f"TIME TAKEN:{time.time()-time_start}")


