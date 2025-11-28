from channels.generic.websocket import AsyncJsonWebsocketConsumer
from ..models.room_model import Room
from django.contrib.auth.models import User
from django.db.models import Q
from asgiref.sync import sync_to_async
from ..logger import logger



class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def sendNotification(self,event):
        await self.send_json(content=event)

    async def connect(self):
        await self.accept()
        
        if self.scope["username"]==None:
            await self.close()
            return

        print(f"✅✅Notification channel connected")
        self.group_name=f"Notification_channel_{self.scope["user_id"]}"
       
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # await self.channel_layer.group_send(
        #     self.group_name,
        #     {
        #         "type":"sendNotification",
        #         "task":"notification",
        #         "notify":"connected"
        #     }
        # )

    async def disconnect(self, code):
        # logger.info(f"🔴 Disconnected: {self.channel_name} from {self.group_name}")
        print(f"nottification channel closed❌❌")
        await self.close()