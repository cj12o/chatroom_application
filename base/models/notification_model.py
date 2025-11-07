from django.db import models,transaction
from django.dispatch import receiver
from .message_model import Message
from .room_model import Room
from core.celery import sendNotificationToWs
from channels.layers import get_channel_layer
from concurrent.futures import ThreadPoolExecutor
from django.contrib.auth.models import User
from django.db.models import Q,signals
import asyncio



# def getisRoomMemeber(username:str,room_name:str)->bool:
#     """return true if admin or mod or member"""
    
#     user=User.objects.get(username=username)
    
#     member=user.room_member.filter(Q(name=room_name))
#     if len(member)>0:
#         return True
#     room=user.author_rooms.filter(Q(name=room_name))
#     if len(room)>0:
#         return True
    
#     mod=user.room_moderator.filter(Q(name=room_name))
#     if len(mod)>0:
#         return True

#     return False


# async def sendNotificationToWs(notify_msg:str,id:int,permission:bool):
#     try:
#         if not permission: return
#         """
#         Sends msg to websocket
#         """ 
#         channel_layer=get_channel_layer()
#         await channel_layer.group_send(
#             "Notification_channel",
#             {
#                 "type":"sendNotification",
#                 "task":"notification",
#                 "notify":notify_msg,
#                 "notification_id":id
#             }
#         )
#     except Exception as e:
#         print(f"❌❌Error in  sending msg to w{str(e)}")


class Notification(models.Model):
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE)
    message=models.OneToOneField(to=Message,on_delete=models.CASCADE)
    notify=models.CharField()
    created_at=models.DateTimeField(auto_now_add=True)
    sent_status=models.BooleanField(default=False)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['room','message'], name='unique_message_room_notification')
        ]

#TODO:delete send notification
#TODO:add recomm is ready

@receiver(sender=Message,signal=signals.post_save)
def task_create_notification(sender,instance,created,**kwargs):
    msg=f"""
        Activity in Room : {instance.room.name}
        {instance.author.username}: Posted {instance.message}
    """


    notf=Notification.objects.create(room=instance.room,message=instance,notify=msg)
    notf.save()

    # future=executor.submit(getisRoomMemeber,instance.author.username,instance.room.name)
    
    # future.add_done_callback(lambda f:asyncio.run(sendNotificationToWs(msg,instance.id,future.result())))
    # createNotification.delay(dct)
    
@receiver(signal=signals.post_save,sender=Notification)
def sendNotifications(sender,instance,created,**kwargs):
    sendNotificationToWs.delay(instance.notify)