from ...models.file_log_model import ChatFileLog
import os
from django.conf import settings
from django.db.models import Q
from datetime import datetime,date
base_dir=settings.BASE_DIR

from queue import Queue

def get_file(room_id)->str:  
        """
        method return file path
        """
        
        file=ChatFileLog.objects.filter(Q(room_id=room_id))

        fileobj=file[0]
        chat_file_path=fileobj.fileLocation

        return chat_file_path
        


def get_json_for_celery(q_msg:Queue,q_msg_id:Queue)->dict:
    jsn_msg={}
    
    for idx in range(0,q_msg_id.qsize()):
        jsn_msg[str(q_msg_id.get())]=q_msg.get()

    return jsn_msg



    

    