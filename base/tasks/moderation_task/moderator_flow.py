import logging
from django.conf import settings
import os
from celery import shared_task
import joblib
from django.db.models import Q


"""setuped to run every k minutes"""
def moderate(corpus:list[tuple[int,str]])->list[int]:
    from base.views.logger import logger
    from base.tasks.moderation_task.load_model import VECTORIZER,MODEL
    
    """model prediction gets returned"""
    try:
        
        results_vec={}
        for id,text in corpus:
            chat_vec=VECTORIZER.transform([text])
            result=MODEL.predict(chat_vec)[0]
            results_vec[id]=result
        

        results_to_send=[] #"ids that are toxic
        for k,v in results_vec.items():
            if v==0:
                "case : non-toxic"
                continue

            else:
                "case : toxic"
                results_to_send.append(k)
        print(f"✅✅Results from model:{results_to_send}")
        return results_to_send

    except Exception as e:
        print(f"ERROR IN moderate :{str(e)}")
        logger.error(e)
        



@shared_task
def start_moderation():
    from base.models import Message
    from base.views.logger import logger
    """changes message content"""
    try:
       
        qs=Message.objects.filter(Q(is_moderated=False)).exclude(Q(author__username="agent"))[:10]
        
        if len(qs)<1:
            logger.info("No message to moderate")
            return
        
        corpus=[(msg.id,msg.message) for msg in qs]
        result=moderate(corpus=corpus)

        new_message=f"🛡️ Removed by Automatic room moderation ,message was found to be :toxic"

        for message_id in result:
            msg=Message.objects.get(id=message_id)
            msg.message=new_message
            msg.is_moderated=True
            
        
        
    except Exception as e:
        print(f"ERROR IN START_mod :{str(e)}")
        logger.error(e)



