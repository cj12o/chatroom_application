from celery import shared_task
import schedule
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain.messages import AnyMessage,SystemMessage,ToolMessage,HumanMessage
# @shared_task
# async def fn():
#    pass
from .models.file_log_model import MessageSummerizedStatus
from .models.message_model import Message
from .views.Rag.perpFiles import get_file
from queue import Queue

load_dotenv()

llm=ChatOpenAI(
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM"),
    api_key=os.getenv("LLM_API_KEY")
)

@shared_task
def add_summerize_task(json_msg:dict):
    """
    param->queue of messages
    step 1) get file path from db
    2) 
    """

    corpus=""
    flag=True
    file_path=None
    for k,v in json_msg.items():
        print(f"Key val:{k}")
        chat_obj=Message.objects.get(id=int(k))
        chat_obj.messagesummerizedstatus.status=True
        chat_obj.save()
        if flag:
            file_path=chat_obj.room.chatfilelog.fileLocation.path

        corpus=corpus+"\n"+v

    print(f"corpus:{corpus}")
    PROMPT_TEMPLATE=f"""

    You are an AI assistant tasked with summarizing a conversation in a chatroom.
    Please follow these guidelines:
    - If chats are empty no need to summarize.
    - Focus primarily on summarizing the chats.
    - The goal is to create a concise summary that captures key details and the overall mood and direction of the conversation.
    - summary should be of maximum 30 to 40 words.
    
    Here are the chats:
    {corpus}
    """

    result=llm.invoke([SystemMessage(content=PROMPT_TEMPLATE)])
    print(f"LLM summery:{result.content}")

    print(f"🥅🥅File path:{file_path}")
    with open(file_path,"a") as f:
        f.write("\n"+result.content)
    

    

