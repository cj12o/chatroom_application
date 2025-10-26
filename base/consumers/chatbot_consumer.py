from channels.generic.websocket import AsyncWebsocketConsumer
from base.views.userRecommendation.llm import llm
import asyncio
import json
import uuid
from base.task import createDoc

from asgiref.sync import sync_to_async

#diff thread pool
createDoc=sync_to_async(createDoc,thread_sensitive=False)

class LlmConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("✅ Chatbot connected")

        self.group_name = "llmgrp"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        #todo:parellism for  create doc
        asyncio.create_task(createDoc(1))
        # createDoc(id=pk)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print("❌ Chatbot disconnected")

    async def receive(self, text_data):
        print(f"Recieved :{text_data}")
        unique_id=uuid.uuid4()

        """
        Called when the client sends a message.
        text_data = user's question.
        """
        print(f"Received prompt: {text_data} unique_id={1}")
        await self.send(text_data=json.dumps({"token":text_data,"id":str(unique_id),"isQuestion":True}))
        
        loop = asyncio.get_event_loop()
        
        resp = await loop.run_in_executor(None, lambda: llm.stream(text_data))

        
        for token in resp:
            await self.send(text_data=json.dumps({"token": token.content,"id":str(unique_id)}))

            await asyncio.sleep(0.01)

        await self.send(text_data=json.dumps({"status": "done"}))
