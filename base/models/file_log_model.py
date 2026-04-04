from django.db import models
from .room_model import Room
from .message_model import Message

from django.db.models  import signals,Q
from django.dispatch import receiver
from ..logger import logger


class ChatFileLog(models.Model):
    room=models.OneToOneField(to=Room,on_delete=models.CASCADE)
    lastSummerized=models.DateTimeField(auto_now=True)
    summary_text=models.TextField(default="",blank=True)

    @classmethod
    def get_summary(cls,room_id)->str:
        """Returns the summary text for a given room"""
        try:
            return cls.objects.get(room_id=room_id).summary_text
        except cls.DoesNotExist:
            logger.error(f"ChatFileLog not found for room_id: {room_id}")
            return ""

    @classmethod
    def append_summary(cls,room_id,text:str)->None:
        """Appends new summary text for a given room"""
        try:
            log=cls.objects.get(room_id=room_id)
            log.summary_text=(log.summary_text+"\n"+text).strip()
            log.save(update_fields=["summary_text","lastSummerized"])
        except cls.DoesNotExist:
            logger.error(f"ChatFileLog not found for room_id: {room_id}")


class MessageSummerizedStatus(models.Model):
    message=models.OneToOneField(to=Message,on_delete=models.CASCADE)
    status=models.BooleanField(default=False,null=False)


    @classmethod
    def get_list_unsummerized(cls):
        qs=cls.objects.filter(Q(status=False)).values()[:10]
        return [q.message for q in qs]


