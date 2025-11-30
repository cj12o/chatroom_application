from django.db import models
from django.contrib.auth.models import User 

from .room_model import Room
from .message_model import Message
from django.db.models import signals
from django.dispatch import receiver
from channels.layers import get_channel_layer
import asyncio
from ..threadPool import ThreadPoolManager
from ..logger import logger

class Poll(models.Model):
    message=models.ForeignKey(to=Message,on_delete=models.CASCADE)
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE)
    author=models.ForeignKey(to=User,on_delete=models.CASCADE)
    question=models.TextField()
    choices=models.JSONField(default=dict)
    created_at=models.DateTimeField(auto_now_add=True)


class PollVote(models.Model):
    poll=models.ForeignKey(to=Poll,on_delete=models.CASCADE,related_name="message_polls")
    user=models.ForeignKey(to=User,on_delete=models.CASCADE)
    choiceSelected=models.IntegerField(null=False,blank=False,default=1)
    created_at=models.DateTimeField(auto_now_add=True)

    

async def connectTows(agent_msg:dict,message_id:int,poll_id:int):
    try:
        channel_layer=get_channel_layer() 
        
        await channel_layer.group_send(
            f"room_{agent_msg["room_id"]}",
            {
                "type":"chat_message",
                "tool_called":agent_msg["tool_called"],
                "task":"AgentActivity",
                # "message":agent_msg["message"],
                "question":agent_msg["message"]["question"],
                "choices":agent_msg["message"]["options"],
                "parent":None,
                "username":"Agent",
                "message_id":message_id,
                "room_id":agent_msg["room_id"],
                "poll_id":poll_id
                # "status": True
            }
        )
    except Exception as  e:
        logger.error(e)


@receiver(sender=Poll,signal=signals.post_save)
def helers(sender,instance,created,**kwargs):
    try:
        agent_msg={
            'tool_called':'pollGenerator',
            'message':{
                'question':instance.question,
                'options':instance.choices["choices"]
            },
            'room_id':instance.message.id
        }
        # print(f"✅✅POLL GENERATOR POST SAVE SENDING {agent_msg}")
        ThreadPoolManager.get().submit(lambda:asyncio.run(connectTows(agent_msg=agent_msg,poll_id=instance.id,message_id=instance.message.id)))
    except Exception as e:
        logger.error(e)


# {'tool_called': 'pollGenerator', 'message': {'question': 'Which Python updates or features are you most excited about?', 'options': ['New version of Python with significant performance improvements', 'Introduction of new data structures and libraries to enhance productivity']}, 'room_id': 1}