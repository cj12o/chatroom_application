from ...models import ChatFileLog
from django.conf import settings
from django.db.models import Q
from ...logger import logger


base_dir=settings.BASE_DIR


def get_file(room_id)->str:  
    try:
        """
        method return file path
        """
        
        file=ChatFileLog.objects.filter(Q(room_id=room_id))

        fileobj=file[0]
        chat_file_path=fileobj.fileLocation

        return chat_file_path
    except Exception as e:
        logger.error(f"Error in get_file: {e}")
        


    

    