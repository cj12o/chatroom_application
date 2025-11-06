import os
from celery import Celery
from django.db.models  import signals,Q
from django.dispatch import receiver
from django.db  import transaction
from channels.layers import get_channel_layer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


app=Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()



from celery import shared_task
import schedule
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain.messages import AnyMessage,SystemMessage,ToolMessage,HumanMessage
import asyncio

load_dotenv()

llm=ChatOpenAI(
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM"),
    api_key=os.getenv("LLM_API_KEY")
)

@shared_task
def add_summerize_task(json_msg:dict):
    from base.models.file_log_model import MessageSummerizedStatus
    from base.models.message_model import Message
    from base.views.Rag.perpFiles import get_file
    try:
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
        - summary should be of  minimum 30 to maximum 40 words.
        
        Here are the chats:
        {corpus}
        """

        result=llm.invoke([SystemMessage(content=PROMPT_TEMPLATE)])
        print(f"LLM summery:{result.content}")

        print(f"🥅🥅File path:{file_path}")
        with open(file_path,"a") as f:
            f.write("\n"+result.content)
        
    except Exception as e:
        print(f"Error in add_summerize_task:{str(e)}")



# @shared_task
# def moderate(json_chats:dict):
    
    
#     for k,v in json_chats.items():


@shared_task(autoretry_for=(), max_retries=0)
def createNotification(json:dict):
    from base.models.notification_model import Notification
    from base.models.room_model import Room
    from base.models.message_model import Message
    try:
        with transaction.atomic():
            room=Room.objects.get(id=json["room_id"])
            message=Message.objects.get(id=json["message_id"])
            notification=Notification.objects.create(room=room,message=message)
            notification.notify=json["notify"]
            notification.save()
        
    #integerity error ,due to race condition
    except Exception as e:
        print(f"❌❌ERROR In saving notifocation:{str(e)}")
        pass
        