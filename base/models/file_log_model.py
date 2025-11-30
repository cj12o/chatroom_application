from django.db import models
from .room_model import Room
from .message_model import Message

from django.db.models  import signals,Q
from django.dispatch import receiver
import os
from django.conf import settings
from ..logger import logger



base_dir=settings.BASE_DIR


class ChatFileLog(models.Model):
    room=models.OneToOneField(to=Room,on_delete=models.CASCADE)
    lastSummerized=models.DateTimeField(auto_now=True)
    fileLocation=models.FileField()

    @classmethod
    def get_file(cls,room_id)->str:  
        try:
            "method return file path"
            
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
        qs=cls.objects.filter(Q(status=False)).values()[:10]
        return [q.message for q in qs]



@receiver(signals.post_save, sender=Message)
def signal_receiver(sender,instance,created,**kwargs):
    try:
        if not created:
            return
        qs=MessageSummerizedStatus.objects.filter(Q(message__id=instance.id))
        if len(qs)>0:
            return
        MessageSummerizedStatus.objects.create(message=instance)
    except Exception as e:
        logger.error(e)


@receiver(signals.post_save, sender=Room)
def create_chat_file(sender, instance, created, **kwargs):
    """
    Room creation signal -> chat file creation
    """
    try:
        if not created:
            return

        folder_path = os.path.join(base_dir, "media/text_rag_files")
        os.makedirs(folder_path, exist_ok=True)      # ensure folder exists

        chat_file_path = os.path.join(folder_path, f"{instance.id}.txt")

        if not os.path.exists(chat_file_path):
            # actually create the file
            with open(chat_file_path, "w", encoding="utf-8") as f:
                f.write("")

            ChatFileLog.objects.create(room=instance, fileLocation=chat_file_path)

            logger.info(f"File created at {chat_file_path} for Room {instance.name}")

    except Exception as e:
        logger.error(f"Error creating chat file: {str(e)}")
