from celery import shared_task
from channels import layers
from asgiref.sync import async_to_sync
from django.db import transaction

async def sendNotificationToWs(json:dict):
    "sends notification to web socket "
    from base.logger import logger
    try:
        to_send={
            "type":"sendNotification",
            "task":"notification",
            "notify":json["notify"],
            "notification_id":json["id"],
            "room_id":json["room_id"]
        }
        channel_layer=layers.get_channel_layer()   
        for id in json["members"]:
            channel_layer,
            await channel_layer.group_send(
                group=f"Notification_channel_{id}",
                message=to_send
            )

    except Exception as e:
        logger.error(e)
        print(f"❌❌Error in  sending msg to ws {str(e)}")


@shared_task()
def SendNotification(json:dict):
    async_to_sync(sendNotificationToWs)(json)


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

