from django.db import models
from ..models  import Room
from django.dispatch import receiver
from django.db.models import Q,signals
from django.db import transaction
import time
from ..logger import logger
class VectorDbAdditionStatus(models.Model):
    room=models.ForeignKey(to=Room,related_name="room_vectordb_add_status",on_delete=models.CASCADE)
    status=models.BooleanField(default=False)


##if server crashses then using this db model we can repopoulate or in future use batches 

@receiver(sender=Room,signal=signals.post_save)
def addToVectorDb(sender,instance,created,**kwargs):
    try:
        if not created: return
        VectorDbAdditionStatus.objects.create(room=instance)
    except Exception as e:
        logger.error(e)
