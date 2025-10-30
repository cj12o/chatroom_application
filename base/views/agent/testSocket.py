from django.contrib.auth.models import User
from websockets.asyncio.client import connect
import websockets
import json
from rest_framework.authtoken.admin import Token
from asgiref.sync import sync_to_async,async_to_sync
import os


def getToken():
    print("✌️✌️Get token called")
    user=User.objects.get(username="Agent")
    token,created=Token.objects.get_or_create(user=user)
    print(f"token={token}")
    return token

getToken=sync_to_async(getToken,thread_sensitive=False)

async def connectTows(agent_msg:str):
    print(f"🥅🥅called Connect to ws")
    token=await getToken()
    print(f"🗼🗼LLM TOKEN{token}")
    uri=os.getenv("WEBSOCKET_URI")+str(token)
    
    print(f"🗼🗼URI:{uri}")
    async with connect(uri=uri,origin="http://127.0.0.1:8000/",open_timeout=200) as websocket:
        try:
            newReply = {
                "message": agent_msg,
                "parent": None,
            }               
            msg=json.dumps(newReply)
            print(f"To send {agent_msg}")
            await websocket.send(text=True,message=msg)
            
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Error in ws:{e}")
        


    
