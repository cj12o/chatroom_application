from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User
from base.models.room_model import Room
from base.models.message_model import Message,Vote
from base.models.poll_model import Poll
from base.services.room_services import get_room_name
from channels.db import database_sync_to_async
import json
from ..logger import logger
from base.services.message_services import saveMessage,vote_operation,savePoll
from base.services.user_services import set_user_online_status
# example scope=>
# scope:Socket:{'type': 'websocket', 'path': '/ws/chat/12/', 'raw_path': b'/ws/chat/12/', 'root_path': '', 'headers': [(b'host', b'127.0.0.1:8000'), (b'connection', b'Upgrade'), (b'pragma', b'no-cache'), (b'cache-control', b'no-cache'), (b'user-agent', b'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'), (b'upgrade', b'websocket'), (b'origin', b'http://localhost:5173'), (b'sec-websocket-version', b'13'), (b'accept-encoding', b'gzip, deflate, br, zstd'), (b'accept-language', b'en-US,en;q=0.9,en-IN;q=0.8'), (b'sec-websocket-key', b'NpwaBdhav7PJ41+DQzpnKg=='), (b'sec-websocket-extensions', b'permessage-deflate; client_max_window_bits')], 'query_string': b'', 'client': ['127.0.0.1', 63479], 'server': ['127.0.0.1', 8000], 'subprotocols': [], 'asgi': {'version': '3.0'}, 'cookies': {}, 'session': <django.utils.functional.LazyObject object at 0x000002261FC4EE40>, 'user': <channels.auth.UserLazyObject object at 0x000002261FC4EF90>, 'path_remaining': '', 'url_route': {'args': (), 'kwargs': {'q': '12'}}}




maintain_user_visibility_fn=database_sync_to_async(set_user_online_status)
get_room_name_fn=database_sync_to_async(get_room_name)
save_message_fn=database_sync_to_async(saveMessage)
vote_operation_fn=database_sync_to_async(vote_operation)
save_poll_fn=database_sync_to_async(savePoll)



class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def user_status_update(self,event):
        """method that on connect and disconnect send jsn msg to update status"""
        await self.send_json(content=event)


    async def chat_message(self, event):
        try:
            """Called when a message is sent to the group"""
            # print(f"❌❌❌Event:{event}")
           
            # await self.send(text_data=f"Received: {message}")
            await self.send_json(content=event)
        except Exception as e:
            logger.error(f"User error in chat message:{e}")
            
    async def connect(self):
        username = self.scope.get("username")
        user_id = self.scope.get("user_id")

        if username is None:
            await self.accept()
            await self.close(code=4003) # 4003 is 'Forbidden'
            return
        else:
            
            await self.accept()
            # print(f"User:{self.scope['username']}")
            # # print(f"🗼🗼SCOPE:{self.scope}")
            # if self.scope["username"] is None:
            #     await self.close()
            #     return

            # p(f"user:{self.scope["username"]}")
            if self.scope.get("url_route",{}).get("kwargs",{}).get("q"):
                self.room_id = self.scope["url_route"]["kwargs"]["q"]  
                self.room_name = await get_room_name_fn(int(self.room_id))
                self.room_group = f"room_{self.room_id}"

                await self.channel_layer.group_add(
                    self.room_group,
                    self.channel_name
                )

                await self.channel_layer.group_send(
                    self.room_group,
                    {
                        "type": "chat_message",
                        "task":"user_status_update",
                        "message":"",   
                        "file":"",
                        "image":"",
                        "username":username,
                        "status": True
                    }
                )

                # print(f"✅ Connected: {self.channel_name} joined {self.room_group}")
                await maintain_user_visibility_fn(username,True)
        


    async def receive(self,text_data):
        try:
            # p(f"Scope:{self.scope}")

            # print(f"📩 Received from {self.channel_name}")
            data=json.loads(text_data)
        
            #task is vote operation
            if "task" in data and data["task"]=="vote":
                if data["status"]=="subtractVote":

                    operation_done=await vote_operation_fn(data["vote_author"],data["message_id"],data["vote_type"],self.room_id,data["status"])

                    await self.channel_layer.group_send(
                        self.room_group,
                        {
                            "type": "chat_message",
                            "status":"subtractVote",
                            "task":"vote",  
                            "operation_done":operation_done,
                            "vote_author":data["vote_author"],
                            "message_id":data["message_id"],
                            "username":self.scope["username"],
                            "vote_type":data["vote_type"],
                        }
                    )

                elif data["status"]=="addVote":
                    
                    operation_done=await vote_operation_fn(data["vote_author"],data["message_id"],data["vote_type"],self.room_id,data["status"])

                    await self.channel_layer.group_send(
                        self.room_group,
                        {
                            "type": "chat_message",
                            "status":"addVote",
                            "task":"vote",  
                            "operation_done":operation_done,
                            "vote_author":data["vote_author"],
                            "message_id":data["message_id"],
                            "username":self.scope["username"],
                            "vote_type":data["vote_type"]
                        }
                    )

                #add to db
            elif "task" in data and data["task"]=="AgentActivity":
                if data["tool_called"]=="pollGenerator":
                    room_id=int(self.scope["url_route"]["kwargs"]["q"])
                    username=self.scope["username"]
            
                    message_id=await save_poll_fn(room_id=room_id,username=username,message=data["message"],parent=data["parent"])
                else:
                    room_id=int(self.scope["url_route"]["kwargs"]["q"])
                    username=self.scope["username"]
                    ###no reactions,no parents
                    message_id=await save_message_fn(room_id=room_id,username=username,message=data["message"],parent=data["parent"])
                    
                await self.channel_layer.group_send(
                    self.room_group,
                    {
                        "type":"chat_message",
                        "tool_called":data["tool_called"],
                        "task":data["task"],
                        "message": data["message"],  
                        "parent":data["parent"],
                        "username":self.scope["username"],
                        "message_id":message_id
                        # "status": True
                    }
                )


            else:
            # broadcast to  group:
                #Add to db
                room_id=int(self.scope["url_route"]["kwargs"]["q"])
                username=self.scope["username"]
                ###no reactions,no parents
                message_id=await save_message_fn(room_id=room_id,username=username,message=data["message"],parent=data["parent"])


                await self.channel_layer.group_send(
                    self.room_group,
                    {
                        "type": "chat_message",
                        "task":"chat",
                        "message": data["message"],  
                        "parent":data["parent"],
                        "username":self.scope["username"],
                        "message_id":message_id
                        # "status": True
                    }
                )
                
                
        except Exception as e:
            logger.error(f"Error in receive: {e}")

    

    async def disconnect(self, close_code):
        try:
            if self.scope["username"] is not None:
                await maintain_user_visibility_fn(self.scope["username"],False)

                await self.channel_layer.group_send(
                    self.room_group,
                    {
                        "type": "chat_message",
                        "task": "user_status_update",   
                        "message":"",
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
