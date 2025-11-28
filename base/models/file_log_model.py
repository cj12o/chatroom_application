from django.db import models
from .room_model import Room
from .message_model import Message

from django.db.models  import signals,Q
from django.dispatch import receiver
import os
from django.conf import settings
from base.tasks import add_summerize_task
from ..logger import logger

from redis import Redis

reddis=Redis(host='localhost', port=6379)
K=5

base_dir=settings.BASE_DIR


class ChatFileLog(models.Model):
    room=models.OneToOneField(to=Room,on_delete=models.CASCADE)
    lastSummerized=models.DateTimeField(auto_now=True)
    fileLocation=models.FileField()

    @classmethod
    def get_file(cls,room_id)->str:  
        try:
            """
            method return file path
            """
            
            file=cls.objects.filter(Q(room_id=room_id))

            fileobj=file[0]
            chat_file_path=fileobj.fileLocation

            return chat_file_path
        except Exception as e:
            logger.error(f"Error in get_file: {e}")


class MessageSummerizedStatus(models.Model):
    message=models.OneToOneField(to=Message,on_delete=models.CASCADE)
    status=models.BooleanField(default=False,null=False)



    @classmethod
    def get_list_unsummerized(cls):
        from ..views.Rag.perpFiles import get_json_for_celery
        qs=cls.objects.filter(Q(status=False)).values()[:10]
        return [q.message for q in qs]



@receiver(signals.post_save, sender=Message)
def signal_receiver(sender,instance,created,**kwargs):
    try:
        global reddis
        if created and not instance.is_moderated:
            print(f"🤖🤖🤖SIGNAL RECIEVED ,message:{instance.message}")
            room_id=instance.room.id
            msg_new_obj=MessageSummerizedStatus.objects.create(message=instance)
            reddis.incr(name=f"room_{room_id}",amount=1)
            if reddis.get(f"room_{room_id}")>=K:
                #todo max
                add_summerize_task.delay({room_id:room_id})
                reddis.set(name=f"room_{room_id}",value=0)

    except Exception as e:
        logger.error(e)


@receiver(signals.post_save,sender=Room)
def create_Chat_file(sender,instance,created,**kwargs):
    "room creation signal->chatfile creation"
    try:
        
        if not created:return 
        "init file"
        chat_file_path=os.path.join(base_dir,f"media/text_rag_files/{instance.name}.txt")
        ChatFileLog.objects.update_or_create(room=instance,fileLocation=chat_file_path)
        # fileobj.fileLocation=chat_file_path
        # fileobj.save()
        logger.info(f"file created at {chat_file_path} for Room {instance.name}")
    except Exception as e:
        logger.error(e)