from channels.generic.websocket import AsyncWebsocketConsumer
from base.views.userRecommendation.llm import llm
import asyncio
import json
import uuid
from ..models.file_log_model import ChatFileLog
from ..models.room_model import Room
from langchain.messages import SystemMessage,HumanMessage
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

#diff thread pool
# createDoc=sync_to_async(createDoc,thread_sensitive=False)

SYSTEM_PROMPT=""


def contextGiver(room_id:int,username:str)->None:
    try:
        """
        gives context to chatbot 
        """
        global SYSTEM_PROMPT

        room=Room.objects.get(id=room_id)
        
        location =room.chatfilelog.fileLocation.path
        file_content=""
        
        with open(str(location),"r") as f:
            file_content=f.read()
        
        system_prompt=f"""
        Role:You are a chat room chatbot

        Username:{username}

        Room details:
            Room name:{room.name}
            Room author:{room.author}
            Room moderator:{room.moderator}
            Room description:{room.description}


        Previous converations :
            {file_content}

        Rules:
            -address user with their name.
            -if user query is related to chat room then try to answer their queries from **Previous converations**.
            -if user query is not related to chat room anwer in genric ways .
            -always ask follow up questions.
        """
        SYSTEM_PROMPT=system_prompt
    except Exception as e:
        print(f"❌❌ERROR in chat bot consumer.py context giver func:{str(e)}")

contextGiver=sync_to_async(contextGiver)

class LlmConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        
        await self.accept()

        # if self.scope["username"]==None:
        #     await self.close()
        #     print("❌❌ Chatbot closed unauthenticated user")
        #     return
        
        print("✅ Chatbot connected")

        self.group_name = "llmgrp"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await contextGiver(int(self.scope["url_route"]["kwargs"]["q"]),self.scope["username"])
        
        

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
        

        # resp = await loop.run_in_executor(None, lambda: llm.stream(text_data))
        resp=await loop.run_in_executor(None,lambda:llm.stream([SystemMessage(content=SYSTEM_PROMPT),HumanMessage(text_data)]))
        
        for token in resp:
            await self.send(text_data=json.dumps({"token": token.content,"id":str(unique_id)}))

            await asyncio.sleep(0.01)

        await self.send(text_data=json.dumps({"status": "done"}))
