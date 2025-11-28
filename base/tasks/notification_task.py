from celery import shared_task
from channels import layers
from asgiref.sync import async_to_sync

async def sendNotificationToWs(json:dict):
    "sends notification to web socket "
    from base.views.logger import logger
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

