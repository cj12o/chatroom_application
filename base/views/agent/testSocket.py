# path("ws/chat/<str:q>/",vote_message_consumers.ChatConsumer.as_asgi()),

from django.contrib.auth.models import User
from websockets.asyncio.client import connect
import websockets
import json
from rest_framework.authtoken.admin import Token
from asgiref.sync import sync_to_async,async_to_sync



# `http://127.0.0.1:8000/ws/chat/${id}/?token=${localStorage.getItem("cookie")||""}`},[id])



def getToken():
    print("✌️✌️Get token called")
    user=User.objects.get(username="Agent")
    token,created=Token.objects.get_or_create(user=user)
    print(f"token={token}")
    return token

getToken=sync_to_async(getToken,thread_sensitive=False)

async def connectTows():
    print(f"🥅🥅called Connect to ws")
    token=await getToken()
    print(f"🗼🗼LLM TOKEN{token}")
    uri=f"ws://127.0.0.1:8000/ws/chat/1/?token={str(token)}"
    
    # socket=websockets.connect(uri=uri)
    # newReply = {
    #     "message": "Send from agent",
    #     "parent": None,
    # }
    # print(f"Sending .... {json.dumps(newReply)}")
    # socket.send(text=True,message=json.dumps(newReply))
    print(f"🗼🗼URI:{uri}")
    async with connect(uri=uri,origin="http://127.0.0.1:8000/",open_timeout=200) as websocket:
        try:
            newReply = {
                "message": "Send from agent",
                "parent": None,
            }               
            msg=json.dumps(newReply)
            print(f"To send {msg}")
            await websocket.send(text=True,message=msg)
            
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Error in ws:{e}")
        # finally:
        #     await websocket.close()


    
