from celery import shared_task

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
        room_id=int(json_msg["room_id"])
        corpus=""
        file_path=ChatFileLog.get_file(room_id)

        msgs=Message.objects.filter(Q(room_id=room_id) & Q(messagesummerizedstatus__status=False)).update(messagesummerizedstatus__status=False)
        
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
        print(f"LLM summery:{result.content}")

        print(f"🥅🥅File path:{file_path}")
        with open(file_path,"a") as f:
            f.write("\n"+result.content)
        
    except Exception as e:
        print(f"Error in add_summerize_task:{str(e)}")
        logger.fatal(f"Error in add_summerize_task:{str(e)}")