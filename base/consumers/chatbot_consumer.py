from channels.generic.websocket import AsyncWebsocketConsumer
from base.views.userRecommendation.llm import llm
import asyncio
import json
import uuid
from ..models.room_model import Room
from langchain.messages import SystemMessage,HumanMessage
from asgiref.sync import sync_to_async
#diff thread pool
# createDoc=sync_to_async(createDoc,thread_sensitive=False)
from ..logger import logger

SYSTEM_PROMPT=""
HUMAN_PROMPT=""

def contextGiver(room_id:int,username:str)->None:
    try:
        from base.logger import logger
        """
        gives context to chatbot 
        """
        global SYSTEM_PROMPT,HUMAN_PROMPT

        room=Room.objects.get(id=room_id)
        
        location =room.chatfilelog.fileLocation.path
        file_content=""
        
        with open(str(location),"r") as f:
            file_content=f.read()
        
        system_prompt=f"""
        Role:You are a chat room chatbot

        Room details:
            Room name:{room.name}
            Room author:{room.author}
            Room moderator:{room.moderator}
            Room description:{room.description}


        Previous converations :
            {file_content}

        Rules:
            -always greet and address user with their name.
            -if user query is related to chat room then try to answer their queries from **Previous converations**.
            -if user query is not related to chat room anwer in genric ways .
            -always ask follow up questions.
        """
       


        human_prompt=f"""
        name of the user :{username}

        query:
        """

        SYSTEM_PROMPT=system_prompt
        HUMAN_PROMPT=human_prompt
        # print(f"SYSTEM_PROMPT:{SYSTEM_PROMPT}")

    except Exception as e:
        logger.error(f"ERROR in chat bot consumer.py context giver func:{str(e)}")



def get_room_name(room_id:int):
    room=Room.objects.get(id=room_id)
    return room.name

get_room_name=sync_to_async(get_room_name)
contextGiver=sync_to_async(contextGiver)

class LlmConsumer(AsyncWebsocketConsumer):
    group_name = ""
    async def connect(self):
        
        await self.accept()
        print(f"SCOPE:{self.scope}")
        if self.scope["username"] is None:
            await self.close()
            logger.error("❌❌ Chatbot closed unauthenticated user")
            return
        
        # print("✅ Chatbot connected")

        self.room_id = self.scope["url_route"]["kwargs"]["q"]
        self.room_name = await get_room_name(int(self.room_id))
        self.room_chatbot_group = f"room_chatbot_{self.room_id}"
        
        await self.channel_layer.group_add(
            self.room_chatbot_group,
            self.channel_name
        )

        await contextGiver(int(self.scope["url_route"]["kwargs"]["q"]),self.scope["username"])
        
        ##Send greet
        unique_id=uuid.uuid4()
        loop = asyncio.get_event_loop()
        

        # resp = await loop.run_in_executor(None, lambda: llm.stream(text_data))

        resp=await loop.run_in_executor(None,lambda:llm.stream([SystemMessage(content=f"Greet the user using their name, username:{self.scope["username"]} ")]))
        
        for token in resp:
            await self.send(text_data=json.dumps({"token": token.content,"id":str(unique_id),"status":"firstMsg"}))

            await asyncio.sleep(0.01)

        await self.send(text_data=json.dumps({"status": "done"}))



    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_chatbot_group,
            self.channel_name
        )
        logger.info("❌ Chatbot disconnected")

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

        resp=await loop.run_in_executor(None,lambda:llm.stream([SystemMessage(content=SYSTEM_PROMPT),HumanMessage(content=HUMAN_PROMPT+text_data)]))
        
        for token in resp:
            await self.send(text_data=json.dumps({"token": token.content,"id":str(unique_id)}))

            await asyncio.sleep(0.01)

        await self.send(text_data=json.dumps({"status": "done"}))
