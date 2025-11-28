import logging
from django.conf import settings
import os
from celery import shared_task
import joblib
from django.db.models import Q
import asyncio
from asgiref.sync import async_to_sync

async def connectToWs(*args)->None:
    from base.logger import logger
    from channels.layers import get_channel_layer
    try:
        "modded message "
        message,parent,username,message_id,room_id=args
        channel_layer=get_channel_layer()
        await channel_layer.group_send(
            f"room_{room_id}",
            {
                "type": "chat_message",
                "task":"moddedMessage",
                "message": message,  
                "parent":parent,
                "username":username,
                "message_id":message_id
                # "status": True
            }
        )
    except Exception as e:
        logger.error(e)


"""setuped to run every k minutes"""
def moderate(corpus:list[tuple[int,str]])->list[int]:
    from base.logger import logger
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
        



# @shared_task
# def start_moderation():
#     from base.models import Message
#     from base.views.logger import logger
#     """changes message content"""
#     try:
       
#         qs=Message.objects.filter(Q(is_moderated=False)).exclude(Q(author__username="agent"))[:10]
        
#         if len(qs)<1:
#             logger.info("No message to moderate")
#             return
        
#         corpus=[(msg.id,msg.message) for msg in qs]
#         result=moderate(corpus=corpus)

#         new_message=f"🛡️ Removed by Automatic room moderation ,message was found to be :toxic"

#         for message_id in result:
#             msg=Message.objects.get(id=message_id)
#             msg.message=new_message
#             msg.is_moderated=True
#             msg.save()
#             if msg.parent!=None:
#                 asyncio.run(connectToWs(msg=msg.parent,parent=msg.parent.id,msg_id=msg.id,username=msg.author.username,room_id=msg.room.id))  
#             else:
#                 asyncio.run(connectToWs(msg=msg.parent,parent=None,msg_id=msg.id,username=msg.author.username,room_id=msg.room.id))  

            
            
        
        
#     except Exception as e:
#         print(f"ERROR IN START_mod :{str(e)}")
#         logger.error(e)



@shared_task
def start_moderation():
    from base.models import Message
    from base.logger import logger
    try:
        
        qs = (
            Message.objects.filter(is_moderated=False)
            .exclude(author__username="agent")
            .order_by("id")[:10]
        )

        if not qs:
            logger.info("No messages to moderate")
            return

        
        corpus = [(msg.id, msg.message) for msg in qs]

        toxic_ids = moderate(corpus)

    
        replaced_msg = "🛡️ Removed by Automatic room moderation, message was found to be toxic."

        for msg_id in toxic_ids:
            msg = Message.objects.get(id=msg_id)

            parent_id = msg.parent.id if msg.parent else None
            username = msg.author.username
            room_id = msg.room.id

            
            msg.message = replaced_msg
            msg.is_moderated = True
            msg.save()

            
            async_to_sync(connectToWs)(
                replaced_msg,     # message
                parent_id,        # parent
                username,         # username
                msg_id,           # message_id
                room_id,          # room_id
            )

        logger.info(f"Moderated {len(toxic_ids)} messages.")

    except Exception as e:
        logger.error(f"ERROR in start_moderation: {str(e)}")
