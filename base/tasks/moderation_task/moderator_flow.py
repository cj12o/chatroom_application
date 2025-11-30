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
    """model prediction gets returned"""
    try:
        from base.logger import logger
        from base.tasks.moderation_task.load_model import VECTORIZER,MODEL
    
        
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
    "start moderation "
    from base.models import Message
    from base.logger import logger
    from base.models.Room_Moderation_model import ModerationType
    try:
        
        qs = (
            Message.objects
            .filter(Q(is_moderated=False)&Q(is_semi_moderated=False))
            .filter(Q(room__room_moderation_type__moderation_type=-1)|Q(room__room_moderation_type__moderation_type=-2))
            .exclude(author__username="agent")
            .order_by("id")[:10]
        )

        if not qs or len(qs)<1:
            logger.info("No messages to moderate")
            return

        
        corpus = [(msg.id, msg.message) for msg in qs]
        print(f"Corpus:{corpus}")
        toxic_ids = moderate(corpus)

    
        replaced_msg = "Removed by Automatic room moderation, message was found to be against guidlines."

        for msg_id in toxic_ids:
            msg = Message.objects.get(id=msg_id)

            parent_id = msg.parent.id if msg.parent else None
            username = msg.author.username
            room_id = msg.room.id



    
            if msg.room.room_moderation_type.moderation_type==ModerationType.Auto:
                Message.objects.filter(id=msg_id).update(message=replaced_msg, is_moderated=True,is_unsafe=True)
               
                async_to_sync(connectToWs)(
                    replaced_msg,     # message
                    parent_id,        # parent
                    username,         # username
                    msg_id,           # message_id
                    room_id,          # room_id
                )

            elif msg.room.room_moderation_type.moderation_type==ModerationType.SemiAuto:
                Message.objects.filter(id=msg_id).update(is_semi_moderated=True,is_flaged_as_unsafe=True)
                

        msg_ids=[msg_id for msg_id,_ in corpus if msg_id not in toxic_ids]
            # if msg_id in toxic_ids: continue
        Message.objects.filter(id__in=msg_ids).update(is_moderated=True)
            
        logger.info(f"Moderated {len(toxic_ids)} messages.")

    except Exception as e:
        logger.error(f"ERROR in start_moderation: {str(e)}")
