from django.db import models
from .room_model import Room
from django.contrib.auth.models import User 
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
import asyncio

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

# async def connectToWs(tool_called:str,message:str,message_id:int,room_id:int,parent=None):
#     try:

#         channel_layer=get_channel_layer()
#         print(f"👤👤✏️✏️✏️CALLED CONNECT TO ES FOR AGENT")
#         await channel_layer.group_send(
#             f"room_{str(room_id)}",
#             {
#                 "type":"chat_message",
#                 "tool_called":tool_called,
#                 "task":"chat",
#                 "message": message,  
#                 "parent":parent,
#                 "username":"Agent",
#                 "message_id":message_id,
#                 # "status": True
#             }
#         )
#     except Exception  as e:
#         print(f"❌❌ERROR in connect to ws AGENT :{str(e)}")

# @receiver(sender=Message,signal=post_save)
# def sendAgentMsgtoWs(sender,instance,created,**kwargs):
#     if instance.author.username=="Agent":
#         asyncio.run(connectToWs(tool_called="threadGenerator",message=instance.message,message_id=instance.id,room_id=instance.room.id))
