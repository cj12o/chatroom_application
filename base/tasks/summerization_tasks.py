from celery import shared_task
from django.conf import settings
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.messages import SystemMessage

load_dotenv()

llm=ChatOpenAI(
    base_url=settings.LLM_BASE_URL,
    model=settings.LLM_MODEL_NAME,
    api_key=settings.LLM_API_KEY
)



@shared_task
def add_summerize_task(json_msg:dict):
    from base.models import MessageSummerizedStatus,ChatFileLog,Message
    from django.db.models import Q
    from base.logger import logger


    # from base.views.Rag.perpFiles import get_file
    try:
        """
        param->queue of messages
        step 1) get file path from db
        2) 
        """
        logger.info(f"Summerization task started for room_id:{json_msg["room_id"]}")
        room_id=int(json_msg["room_id"])
        corpus=""
        file_path=ChatFileLog.get_file(room_id)

        msgs=Message.objects.filter(Q(room__id=room_id) & Q(messagesummerizedstatus__status=False)&Q(is_moderated=True)&Q(is_unsafe=False))
        
        for msg in msgs:
            corpus=corpus+"\n"+msg.message

        print(f"corpus:{corpus}")
        PROMPT_TEMPLATE=f"""

        You are an AI assistant tasked with summarizing a conversation in a chatroom.
        Please follow these guidelines:
        - If chats are empty no need to summarize.
        - Focus primarily on summarizing the chats.
        - The goal is to create a concise summary that captures key details and the overall mood and direction of the conversation.
        - summary should be of  minimum 30 to maximum 40 words.
        
        Here are the chats:
        {corpus}
        """

        result=llm.invoke([SystemMessage(content=PROMPT_TEMPLATE)])
        # print(f"LLM summery:{result.content}")

        # print(f"🥅🥅File path:{file_path}")
        MessageSummerizedStatus.filter(Q(room__id=room_id)&Q(status=False)).update(status=True)
        with open(file_path,"a") as f:
            f.write("\n"+result.content)
        logger.info(f"Summerization task completed for room_id:{json_msg['room_id']}")
        
    except Exception as e:
        print(f"Error in add_summerize_task:{str(e)}")
        logger.fatal(f"Error in add_summerize_task:{str(e)}")