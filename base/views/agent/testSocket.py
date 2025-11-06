from django.contrib.auth.models import User
from websockets.asyncio.client import connect
import websockets
import json
from rest_framework.authtoken.admin import Token
from asgiref.sync import sync_to_async,async_to_sync
import os
import asyncio

from ...models.room_model import Room
from ...models.message_model import Message
from ...models.poll_model  import Poll
from datetime import date,datetime
from channels.layers import get_channel_layer

def getToken():
    print("✌️✌️Get token called")
    user=User.objects.get(username="Agent")
    token,created=Token.objects.get_or_create(user=user)
    print(f"token={token}")
    return token

getToken=sync_to_async(getToken,thread_sensitive=False)

def savePolltoDb(room_id:int,username:str,message:dict,parent:int=None):
    try:
        room=Room.objects.get(id=room_id)
        author=User.objects.get(username=username)
        
        msg=Message.objects.create(room=room,author=author,message="")
        if parent!=None:
            parent_msg=Message.objects.get(id=parent)
            msg.parent=parent_msg

        msg.save()

        author=User.objects.get(username="Agent")
        room=Room.objects.get(id=room_id)

        new_poll=Poll.objects.create(message=msg,author=author,room=room,question=message["question"],choices={"choices":message["options"]})
        # new_poll.question=message["question"]
        # new_poll.choices={"choices":message["choices"]}
        new_poll.save()
        return (msg.id,new_poll.id)
    except Exception as e:
        print(f"❌❌🪨🪨POLL NOT SAVED,error:{str(e)}")


savePolltoDb=sync_to_async(savePolltoDb)


async def connectTows(agent_msg:dict):

    print(f"🥅🥅called Connect to ws")

    newReply = {
        "message": agent_msg["message"],
        "task":"AgentActivity",
        "tool_called":agent_msg["tool_called"] if len(agent_msg)>1 else None,
        "parent": None,
    }   
    channel_layer=get_channel_layer() 
    # newReply_str=json.dumps(newReply)

    message_id,poll_id=await savePolltoDb(room_id=agent_msg["room_id"],username="Agent",message=agent_msg["message"])
    
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
    
