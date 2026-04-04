from celery import shared_task


@shared_task
def add_summerize_task(json_msg:dict):
    from base.models import MessageSummerizedStatus,ChatFileLog,Message
    from django.db.models import Q
    from base.logger import logger
    from base.services.prompt_services import get_prompt
    from base.services.llm_services import get_model
    from django.conf import settings
    from langchain.messages import HumanMessage, SystemMessage
    from base.services.message_services import get_lastest_moderated_unsummerized_message

    try:
        """
        param->queue of messages
        step 1) get file path from db
        2) 
        """
        logger.info(f"Summerization task started for room_id:{json_msg['room_id']}")
        room_id=int(json_msg["room_id"])
        message_lst=get_lastest_moderated_unsummerized_message(room_id,settings.SUMMERIZATION_BATCH_SIZE)
        if not message_lst or len(message_lst)<1:
            logger.info(f"No messages to summerize for room_id:{room_id}")
            return
        
        prompt=get_prompt("summerization.md")
        human_prompt=HumanMessage(content="\n".join(message_lst))
        system_prompt=SystemMessage(content=prompt)


        model=get_model(settings.LLM_MODEL_SUMMERIZATION)
        if not model:
            raise Exception("Model not found")
        result=model.invoke([system_prompt,human_prompt])
        print(f"LLM summery:{result.content}")

        MessageSummerizedStatus.objects.filter(Q(room__id=room_id)&Q(status=False)).update(status=True)
        ChatFileLog.append_summary(room_id,result.content)
        logger.info(f"Summerization task completed for room_id:{json_msg['room_id']}")
        
    except Exception as e:
        print(f"Error in add_summerize_task:{str(e)}")
        logger.fatal(f"Error in add_summerize_task:{str(e)}")