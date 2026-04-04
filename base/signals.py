from django.db import models
from base.models import Message,Room,ChatFileLog,MessageSummerizedStatus

from django.db.models  import signals,Q
from django.dispatch import receiver
from base.logger import logger

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
def create_chat_file_log(sender, instance, created, **kwargs):
    """
    Room creation signal -> ChatFileLog row creation
    """
    try:
        if not created:
            return
        ChatFileLog.objects.get_or_create(room=instance)
        logger.info(f"ChatFileLog created for Room {instance.name}")
    except Exception as e:
        logger.error(f"Error creating ChatFileLog: {str(e)}")
