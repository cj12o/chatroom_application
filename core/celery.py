import os
from celery import Celery
from django.db  import transaction


from celery import shared_task
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain.messages import AnyMessage,SystemMessage
from django.conf import settings

from channels import layers
import asyncio
from asgiref.sync import async_to_sync

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


app=Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(packages=['base.tasks.recomm_tasks'])



from dotenv import load_dotenv

load_dotenv()

llm=ChatOpenAI(
    base_url=settings.LLM_BASE_URL,
    model=settings.LLM_MODEL_NAME,
    api_key=settings.LLM_API_KEY
)




@shared_task(autoretry_for=(), max_retries=0)
def createNotification(json:dict):
    from base.models import Notification,Message,Room,PersonalNotification
    
    try:
        with transaction.atomic():
            room=Room.objects.get(id=json["room_id"])
            message=Message.objects.get(id=json["message_id"])
            notification=Notification.objects.create(room=room,message=message,notify=json["notify"])
            notification.populatePersonalNotification()
        json2={
            "notify":json["notify"],
            "id":notification.id,
            "room_id":notification.room.id
        }

    #integerity error ,due to race condition
    except Exception as e:
        print(f"❌❌ERROR In saving notifocation:{str(e)}")
        pass
        
