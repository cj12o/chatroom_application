# from channels.generic.websocket import AsyncJsonWebsocketConsumer



# class NotificationConsumer(AsyncJsonWebsocketConsumer):
#     async def sendNotification(self,event):
#         await self.send_json(content=event)

#     async def connect(self):
#         await self.accept()
        
#         if self.scope["username"] is None:
#             await self.close()
#             return

#         print("✅✅Notification channel connected")
#         self.group_name=f"Notification_channel_{self.scope['user_id']}"
       
#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )

#         # await self.channel_layer.group_send(
#         #     self.group_name,
#         #     {
#         #         "type":"sendNotification",
#         #         "task":"notification",
#         #         "notify":"connected"
#         #     }
#         # )

#     async def disconnect(self, code):
#         # logger.info(f"🔴 Disconnected: {self.channel_name} from {self.group_name}")
#         print("nottification channel closed❌❌")
#         await self.close()

from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # 1. Initialize group_name as None to avoid AttributeErrors in disconnect
        self.group_name = None
        
        # 2. Check if middleware successfully found a user
        # We check .get() to avoid KeyError if the middleware crashed
        username = self.scope.get("username")
        user_id = self.scope.get("user_id")

        if username is None:
            # If guest, we accept then immediately close with a code
            # or just don't accept at all.
            await self.accept() 
            await self.close(code=4003) # 4003 is 'Forbidden'
            return

        # 3. Setup Group
        self.group_name = f"Notification_channel_{user_id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        print(f"✅✅ Notification channel connected for {username}")

    async def disconnect(self, code):
        # 4. Only try to leave group if we actually joined one
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        print("notification channel closed ❌❌")
        # NEVER call self.close() here. It's already closing!

    async def sendNotification(self, event):
        # Channels wraps the event, ensure we send the actual data
        await self.send_json(content=event)