from channels.generic.websocket import AsyncJsonWebsocketConsumer



class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        if self.scope["username"]==None:
            await self.close()
            return

        self.group_name="Notification_channel"

        self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.channel_layer.send(
            self.channel_layer,
            {
                "type":
            }
        )
