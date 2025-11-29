from django.db import models
from .room_model import Room
from django.contrib.auth.models import User 
from django.db.models.signals import post_delete,post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
import asyncio
from ..logger import logger
from redis import Redis
from base.tasks import start_moderation

reddis=Redis(host='localhost', port=6379)
K=5

class Message(models.Model):
    room = models.ForeignKey(to=Room,on_delete=models.CASCADE,related_name="room_message")
    author=models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="author_message")
    message = models.TextField(null=False,blank=False)
    images_msg=models.ImageField(null=True,upload_to="images/")
    file_msg=models.FileField(null=True,upload_to="files/")
    parent=models.ForeignKey(to="self",on_delete=models.CASCADE,null=True,related_name="parent_message")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_moderated=models.BooleanField(default=False)    
    is_unsafe=models.BooleanField(default=False)
    is_flaged_as_unsafe=models.BooleanField(default=False)#semi mod
    is_semi_moderated=models.BooleanField(default=False)
class Vote(models.Model):
    user=models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="user_votes")
    message=models.ForeignKey(to=Message,on_delete=models.CASCADE,related_name="message_votes")
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE,related_name="room_votes")
    vote=models.SmallIntegerField(choices=[(1,"upvote"),(-1,"downvote")])

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['user', 'message','room'], name='unique_user_message_room_vote')
        ]


async def connectToWs(case:int,*args)->None:
    try:
        if case==1:
            room_id,message_id=args
            "delete message "
            channel_layer=get_channel_layer()
            await channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "chat_message",
                    "status":"",
                    "task":"deleteMessage",  
                    "message_id":message_id,
                }
            )
        else:
            "modded message "
            message,parent,username,message_id=args
            channel_layer=get_channel_layer()
            await channel_layer.group_send(
                f"room_{room_id}",
                {
                    "type": "chat_message",
                    "task":"moddedMessage",
                    "message": message,  
                    "parent":parent,
                    "username":username,
                    "message_id":message_id
                    # "status": True
                }
            )
    except Exception as e:
        logger.error(e)


@receiver(sender=Message,signal=post_delete)
def delete_message(sender,instance,**kwargs):
    try:
        asyncio.run(connectToWs(1,instance.room.id,instance.id))
    except Exception as e:
        logger.error(e)


@receiver(sender=Message,signal=post_save)
def send_modded_message(sender,created,instance,**kwargs):
    global K
    try:
        if not created and instance.is_moderated:return
        reddis.incr(name="unmodded",amount=1)
        print(f"Message count:{reddis.get("unmodded")}")
        
        if int(reddis.get("unmodded"))>=K:
            start_moderation.delay()
            print(f"Reached{K}")
            reddis.set(name="unmodded",value=int(reddis.get("unmodded"))-K)

    except Exception as e:
        logger.error(e)

