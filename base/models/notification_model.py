from django.db import models,transaction
from django.dispatch import receiver
from .message_model import Message
from .room_model import Room
from channels.layers import get_channel_layer
from concurrent.futures import ThreadPoolExecutor
from django.contrib.auth.models import User
from django.db.models import Q,signals
import asyncio
from django.utils.timezone import now
from datetime import timedelta
from ..logger import logger
from base.tasks.notification_task import SendNotification,createNotification
"""FLOW OF NOTIFICATION
signal postsave Message-->celery Tak(createNotification)->asyncio (send to ws) -->update sent_status->consumer valides user 
"""



class Notification(models.Model):
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE)
    message=models.ForeignKey(to=Message,on_delete=models.CASCADE)
    notify=models.CharField()
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['room','message'], name='unique_message_room_notification')
        ]

    def populatePersonalNotification(self):
        """a method that creates personal notification for all users in the room"""
        """
        sending to celery :format :
        {
            "notify":notification.message,
            "id":notification.id,
            "room_id":notification.room.id
            "members":[lst of usernames]
        }
        """
        
        try:
            receiver_details={}
            
            receiver_details['members']=[member.id for member in self.room.members.all()]
            # receiver_details['members'].append(self.room.author.id)
        
            receiver_details["id"]=self.id
            receiver_details["room_id"]=self.room.id
            receiver_details["notify"]=self.notify
            #since mods are memebers so ya moderators will also get notification

            PersonalNotification.objects.bulk_create([PersonalNotification(user=user,notification=self) for user in self.room.members.all()])
            SendNotification.delay(receiver_details)
        except Exception as e:
            logger.error(e)

    @classmethod
    def clean(cls):
        """a classmethod that deletes notifications older than 7 Days"""
        try:
            threshold=now()-timedelta(days=7)
            cls.objects.filter(created_at__lt=threshold).delete()
            logger.info("Delete old notification")
        except Exception as e:
            logger.error(e)
                            

class PersonalNotification(models.Model):
    user=models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="personalnotification_user")
    notification=models.ForeignKey(to=Notification,on_delete=models.CASCADE,related_name="personalnotification_notification")
    sent_status=models.BooleanField(default=False)
    mark_read=models.BooleanField(default=False)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['user','notification'], name='unique_user_notification')
        ]

    @classmethod
    def clean(cls):
        """a classmethod that deletes read Notifications """
        try:
            cls.objects.filter(mark_read=True).delete()
            logger.info("Delete read notification")
        except Exception as e:
            logger.error(e)        
    

#TODO:add recomm is ready


@receiver(sender=Message,signal=signals.post_save)
def task_create_notification(sender,instance,created,**kwargs):
    if not created:return
    msg=f"Activity:{instance.author.username}: Posted {instance.message}"
        
    dct={
        "room_id":instance.room.id,
        "message_id":instance.id,
        "notify":msg
    }

    createNotification.delay(dct)