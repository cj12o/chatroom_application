
# from  channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User
from base.models.userprofile_model import UserProfile
from base.models.room_model import Room
from base.models.message_model import Message
from channels.db import database_sync_to_async
import json 
# example scope=>
# scope:Socket:{'type': 'websocket', 'path': '/ws/chat/12/', 'raw_path': b'/ws/chat/12/', 'root_path': '', 'headers': [(b'host', b'127.0.0.1:8000'), (b'connection', b'Upgrade'), (b'pragma', b'no-cache'), (b'cache-control', b'no-cache'), (b'user-agent', b'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'), (b'upgrade', b'websocket'), (b'origin', b'http://localhost:5173'), (b'sec-websocket-version', b'13'), (b'accept-encoding', b'gzip, deflate, br, zstd'), (b'accept-language', b'en-US,en;q=0.9,en-IN;q=0.8'), (b'sec-websocket-key', b'NpwaBdhav7PJ41+DQzpnKg=='), (b'sec-websocket-extensions', b'permessage-deflate; client_max_window_bits')], 'query_string': b'', 'client': ['127.0.0.1', 63479], 'server': ['127.0.0.1', 8000], 'subprotocols': [], 'asgi': {'version': '3.0'}, 'cookies': {}, 'session': <django.utils.functional.LazyObject object at 0x000002261FC4EE40>, 'user': <channels.auth.UserLazyObject object at 0x000002261FC4EF90>, 'path_remaining': '', 'url_route': {'args': (), 'kwargs': {'q': '12'}}}

# TODO: add voice + file


def maintain_user_visibility(username:str,flag:bool):
    """
    sets is_online in userProfile model
    """
    user=UserProfile.objects.get(user__username=username)
    user.is_online=flag
    user.save()


def get_room_name(room_id:int):
    room=Room.objects.get(id=room_id)
    return room.name


def saveToDb(room_id:int,username:str,message:str,reactions:list=[],parent:int=None):
    """message to db"""
    room=Room.objects.get(id=room_id)
    author=User.objects.get(username=username)

    msg=Message.objects.create(room=room,author=author,message=message)
    if parent!=None:
        parent_msg=Message.objects.get(id=parent)
        msg.parent=parent_msg
    
    msg.save()


    


maintain_user_visibility=database_sync_to_async(maintain_user_visibility)
get_room_name=database_sync_to_async(get_room_name)
saveToDb=database_sync_to_async(saveToDb)




class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def user_status_update(self,event):
        """methos that on connect and disconnect send jsn msg to update status"""
        await self.send_json(content=event)


    async def chat_message(self, event):
        try:
            """Called when a message is sent to the group"""
            print(f"❌❌❌Event:{event}")
           
            # await self.send(text_data=f"Received: {message}")
            await self.send_json(content=event)
        except Exception as e:
            print(f"User error in chat message:{e}")
            
    async def connect(self):
        try:
            await self.accept()
            print(f"User:{self.scope["username"]}")

            if self.scope["username"]==None:
                await self.close()
                return

            # print(f"user:{self.scope["username"]}")
            self.room_id = self.scope["url_route"]["kwargs"]["q"]
            self.room_name = await get_room_name(int(self.room_id))
            self.room_group = f"room_{self.room_id}"

            await self.channel_layer.group_add(
                self.room_group,
                self.channel_name
            )

            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type": "chat_message",
                    "message": "user_status_update",   
                    "username":self.scope["username"],
                    "status": True
                }
            )

            print(f"✅ Connected: {self.channel_name} joined {self.room_group}")
            await maintain_user_visibility(username=self.scope["username"],flag=True)
        except Exception as e:
            print(f"❌ Error in connect: {e}")


    async def receive(self,text_data):
        try:
            # print(f"Scope:{self.scope}")

            print(f"📩 Received from {self.channel_name}")
            # if type(text_data)==dict:
            data=json.loads(text_data)
            print(data)


            # broadcast to  group:
            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type": "chat_message",
                    "message": data["message"],  
                    "parent":data["parent"],
                    "username":self.scope["username"],
                    # "status": True
                }
            )
            
            #Add to db
            room_id=int(self.scope["url_route"]["kwargs"]["q"])
            username=self.scope["username"]
            ###no reactions,no parents
            await saveToDb(room_id=room_id,username=username,message=data["message"],parent=data["parent"])

        except Exception as e:
            print(f"❌ Error in receive: {e}")

    

    async def disconnect(self, close_code):
        try:
            if self.scope["username"]!=None:
                await maintain_user_visibility(username=self.scope["username"],flag=False)

                await self.channel_layer.group_send(
                    self.room_group,
                    {
                        "type": "chat_message",
                        # "message": "user_status_update",   
                        "username":self.scope["username"],
                        "status": False
                    }
                )

                await self.channel_layer.group_discard(
                    self.room_group,
                    self.channel_name
                )
            
                print(f"🔴 Disconnected: {self.channel_name} from {self.room_group}")
        except Exception as e:
            print(f"Error in disconnect :{str(e)}")
