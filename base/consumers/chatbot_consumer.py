from channels.generic.websocket import AsyncWebsocketConsumer
from base.services.llm_services import get_model_for_stream
import asyncio
import json
import uuid
from base.models  import Room,ChatFileLog
from asgiref.sync import sync_to_async
from base.services.room_services import get_room_name
from base.services.rate_limiter import check_and_increment
from base.logger import logger

def contextGiver(room_id:int,username:str,query:str)->list:
    try:
        """
        gives context to chatbot
        """
        

        room=Room.objects.get(id=room_id)

        file_content=ChatFileLog.get_summary(room_id)
        
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
        query: {query}
        """
        return [system_prompt,human_prompt]
        # print(f"SYSTEM_PROMPT:{SYSTEM_PROMPT}")

    except Exception as e:
        logger.error(f"ERROR in chat bot consumer.py context giver func:{str(e)}")
        return []





get_room_name_async=sync_to_async(get_room_name)
contextGiver_async=sync_to_async(contextGiver)

class LlmConsumer(AsyncWebsocketConsumer):
    group_name = ""
    async def connect(self):
        username=self.scope.get("username")
        user_id=self.scope.get("user_id")

        if username is None:
            await self.accept()
            await self.close(code=4003)
            logger.error("❌❌ Chatbot closed unauthenticated user")
            return
     
        await self.accept()
        print(f"SCOPE:{self.scope}")
        
        # print("✅ Chatbot connected")
        if self.scope.get("url_route",{}).get("kwargs",{}).get("q"):
            self.room_id = self.scope["url_route"]["kwargs"]["q"]
            self.room_name = await get_room_name_async(int(self.room_id))
            self.room_chatbot_group = f"room_chatbot_{self.room_id}_{user_id}"
            self.username=username
            
            await self.channel_layer.group_add(
                self.room_chatbot_group,
                self.channel_name
            )
            
            ##Send greet
            unique_id=uuid.uuid4()
            

            llm=get_model_for_stream("gpt-4o-mini")
            if llm is None:
                await self.send(text_data=json.dumps({"error": "LLM not found"}))
                return
            systemPrompt=f"Greet the user using their name, username:{username}"
            resp=llm.stream([systemPrompt])
            
            for token in resp:
                print(f"Token:{token}")
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
        # Rate limit LLM calls per user
        user_id = self.scope.get("user_id")
        if user_id:
            allowed = await sync_to_async(check_and_increment)(user_id, "chatbot")
            if not allowed:
                await self.send(text_data=json.dumps({
                    "error": "Rate limit exceeded. Please wait before sending more messages.",
                    "status": "rate_limited"
                }))
                return

        print(f"Received prompt: {text_data} unique_id={1}")
        await self.send(text_data=json.dumps({"token":text_data,"id":str(unique_id),"isQuestion":True}))
        
        
        llm=get_model_for_stream("gpt-4o-mini")
        if llm is None:
            await self.send(text_data=json.dumps({"error": "LLM not found"}))
            return
        
        prompt_lst=await contextGiver_async(self.room_id,self.username,text_data)

        if prompt_lst is None or len(prompt_lst)!=2:
            await self.send(text_data=json.dumps({"error": "Context not found"}))

        resp=llm.stream(prompt_lst)
        
        for token in resp:
            await self.send(text_data=json.dumps({"token": token.content,"id":str(unique_id)}))
            await asyncio.sleep(0.01)
        await self.send(text_data=json.dumps({"status": "done"}))
