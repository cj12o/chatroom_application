from celery import shared_task
from channels import layers
from asgiref.sync import async_to_sync


async def sendNotificationToWs(json: dict):
    "sends notification to web socket"
    from base.logger import logger
    try:
        to_send = {
            "type": "sendNotification",
            "task": "notification",
            "notify": json["notify"],
            "notification_id": json["id"],
            "room_id": json["room_id"]
        }
        channel_layer = layers.get_channel_layer()
        for id in json["members"]:
            await channel_layer.group_send(
                group=f"Notification_channel_{id}",
                message=to_send
            )

    except Exception as e:
        logger.error(f"Error in sending msg to ws {str(e)}")


@shared_task()
def SendNotification(json: dict):
    async_to_sync(sendNotificationToWs)(json)


@shared_task(autoretry_for=(), max_retries=0)
def createNotification(json: dict):
    from base.services.notification_service import create_notification
    from base.logger import logger
    try:
        create_notification(
            room_id=json["room_id"],
            message_id=json["message_id"],
            notify_text=json["notify"]
        )
    except Exception as e:
        logger.error(f"ERROR In saving notification: {str(e)}")
