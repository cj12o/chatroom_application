from channels.generic.websocket import AsyncJsonWebsocketConsumer
from ..models.room_model import Room
from django.contrib.auth.models import User
from django.db.models import Q
from asgiref.sync import sync_to_async


def isAdmin_memeber_mod(room_id:int,username:str)->bool:
    """user verification if user fills theses roles then only recieve notification"""
    user=User.objects.get(username=username)
    admin_lst=user.author_rooms.filter(Q(id=room_id))
    if len(admin_lst)>0:
        return True
    
    memeber_lst=user.room_member.filter(Q(id=room_id))
    if len(memeber_lst)>0:
        return True
    
    mod_lst=user.room_moderator.filter(Q(id=room_id))
    if len(mod_lst)>0:
        return True
    
    return False

isAdmin_memeber_mod=sync_to_async(isAdmin_memeber_mod)
class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def sendNotification(self,event):
        if "room_id" in event:
            flag=await isAdmin_memeber_mod(username=self.scope["username"],room_id=event["room_id"])
            if flag:
                await self.send_json(content=event)

    async def connect(self):
        await self.accept()
        
        if self.scope["username"]==None:
            await self.close()
            return

        print(f"✅✅Notification channel connected")
        self.group_name="Notification_channel"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type":"sendNotification",
                "task":"notification",
                "notify":"connected"
            }
        )

    async def disconnect(self, code):
        print(f"nottification channel closed❌❌")
        await self.close()