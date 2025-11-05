from django.db import models,transaction
from django.db.models import signals
from django.dispatch import receiver
from .message_model import Message
from .room_model import Room
from core.celery import createNotification 
class Notification(models.Model):
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE)
    message=models.OneToOneField(to=Message,on_delete=models.CASCADE)
    notify=models.CharField()
    created_at=models.DateTimeField(auto_now_add=True)
    sent_status=models.BooleanField(default=False)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['room','message'], name='unique_message_room_notification')
        ]

#TODO:delete send notification
#TODO:add recomm is ready

@receiver(sender=Message,signal=signals.post_save)
def task_create_notification(sender,instance,created,**kwargs):
    dct={
        "room_id":instance.room.id,
        "message_id":instance.id,
        "notify":f"{instance.author.username}: Posted {instance.message}"
    }
    print(f"sending TO notify:{dct}")
    createNotification.delay(dct)
    