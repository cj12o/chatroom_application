from django.db import models,transaction
from django.dispatch import receiver
from .message_model import Message
from .room_model import Room
from core.celery import createNotification
from channels.layers import get_channel_layer
from concurrent.futures import ThreadPoolExecutor
from django.contrib.auth.models import User
from django.db.models import Q,signals
import asyncio

"""FLOW OF NOTIFICATION
signal postsave Message-->celery Tak(createNotification)->asyncio (send to ws) -->update sent_status->consumer valides user 
"""


class Notification(models.Model):
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE)
    message=models.ForeignKey(to=Message,on_delete=models.CASCADE)
    notify=models.CharField()
    created_at=models.DateTimeField(auto_now_add=True)
    sent_status=models.BooleanField(default=False)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['room','message'], name='unique_message_room_notification')
        ]

#TODO:delete send notification
#TODO:add recomm is ready


async def sendNotificationToWs(notify_msg:str,notification_id:int,room_id:int):
    try:
        """
        Sends msg to websocket
        """ 
        channel_layer=get_channel_layer()
        await channel_layer.group_send(
            "Notification_channel",
            {
                "type":"sendNotification",
                "task":"notification",
                "notify":notify_msg,
                "notification_id":notification_id,
                "room_id":room_id
            }
        )
        print(f"❌❌NOTIF SEND TO WS")
    except Exception as e:
        print(f"❌❌Error in  sending msg to w{str(e)}")



# @receiver(sender=Message,signal=signals.post_save)
# def task_create_notification(sender,instance,created,**kwargs):
    
#     try:
#         if not created: return #if msg not created
#         print(f"✌️✌️SIGNAL RECIEVED ")
#         msg=f"""
#             Activity in Room : {instance.room.name}
#             {instance.author.username}: Posted {instance.message}
#         """
#         room=Room.objects.get(id=instance.room.id)
#         notf,_=Notification.objects.get_or_create(room=room,message=instance,notify=msg)
#         if not notf.sent_status:
#             asyncio.run(sendNotificationToWs(notification_id=notf.id,notify_msg=notf.notify,room_id=notf.room.id))
#             Notification.objects.filter(Q(id=notf.id))
#             print(f"✌️✌️SIGNAL RECIEVED  message saved {msg}")

#     except Exception as e:
#         print(f"ERROR  IN saving notification :{str(e)}")



@receiver(sender=Message,signal=signals.post_save)
def task_create_notification(sender,instance,created,**kwargs):
    if not created:return
    msg=f"""
        Activity in Room : {instance.room.name}
            {instance.author.username}: Posted {instance.message}
        """
    
    dct={
        "room_id":instance.room.id,
        "message_id":instance.id,
        "notify":msg
    }

    createNotification.delay(dct)