from django.db import models
from .room_model import Room
from .message_model import Message

from django.db.models  import signals,Q
from django.dispatch import receiver
from queue import Queue

from core.celery import add_summerize_task

q=Queue()
msg_id_q=Queue() #queue containe message id
"""
k denotes batch size
"""
k=3

import os
from django.conf import settings
base_dir=settings.BASE_DIR

class ChatFileLog(models.Model):
    room=models.OneToOneField(to=Room,on_delete=models.CASCADE)
    lastSummerized=models.DateTimeField(auto_now=True)
    fileLocation=models.FileField()


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
    
    from  ..views.Rag.perpFiles import get_json_for_celery
    # from ..task import add_summerize_task
    global q,msg_id_q
    

    if created:
        msg_new_obj=MessageSummerizedStatus.objects.create(message=instance)
        q.put(instance.message)
        msg_id_q.put(instance.id)
        print(f"🤖🤖🤖SIGNAL RECIEVED ,message:{instance.message}")
        if q.qsize()==k:
            # add sum to queue 
            json_msg=get_json_for_celery(q_msg=q,q_msg_id=msg_id_q)

            print(f"🥅🥅🥅Sending to task celery {json_msg}")
            add_summerize_task.delay(json_msg)    
         
            # clear global queue
            # msg_id_q.empty()          
           


@receiver(signals.post_save,sender=Room)
def create_Chat_file(sender,instance,**kwargs):
    "init file"
    chat_file_path=os.path.join(base_dir,f"media/text_rag_files/{instance.name}.txt")
    fileobj=ChatFileLog.objects.create(room=instance)
    fileobj.fileLocation=chat_file_path
    fileobj.save()