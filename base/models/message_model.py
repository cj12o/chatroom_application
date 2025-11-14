from django.db import models
from .room_model import Room
from django.contrib.auth.models import User 
from django.db.models.signals import post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
import asyncio
from ..views.logger import logger
class Message(models.Model):
    room = models.ForeignKey(to=Room,on_delete=models.CASCADE,related_name="room_message")
    author=models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="author_message")
    message = models.TextField(null=False,blank=False)
    images_msg=models.ImageField(null=True,upload_to="images/")
    file_msg=models.FileField(null=True,upload_to="files/")
    parent=models.ForeignKey(to="self",on_delete=models.CASCADE,null=True,related_name="parent_message")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Vote(models.Model):
    user=models.ForeignKey(to=User,on_delete=models.CASCADE)
    message=models.ForeignKey(to=Message,on_delete=models.CASCADE)
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE)
    vote=models.SmallIntegerField(choices=[(1,"upvote"),(-1,"downvote")])

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['user', 'message','room'], name='unique_user_message_room_vote')
        ]


async def connectToWs(room_id:int,message_id:int):
    try:
        "delete message "
        channel_layer=get_channel_layer()
        await channel_layer.group_send(
            f"room_{room_id}",
            {
                "type": "chat_message",
                "status":"addVote",
                "task":"deleteMessage",  
                "message_id":message_id,
            }
        )
    except Exception as e:
        logger.error(e)


@receiver(signal=post_delete)
def delete_message(sender,instance,**kwargs):
    try:
        channel_layer=get_channel_layer()
        asyncio.run(connectToWs(instance.room.id,instance.id))
    except Exception as e:
        logger.error(e)
