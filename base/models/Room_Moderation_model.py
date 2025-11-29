from django.db import models
from ..logger import logger
from django.db.models import Q,Case,When,Value

class RoomModerationType(models.Model):
    room=models.ForeignKey(to="Room",on_delete=models.CASCADE,related_name="room_moderation_type")
    is_auto_moderated=models.BooleanField(default=False)
    is_semi_auto_moderated=models.BooleanField(default=True)
    is_manually_moderated=models.BooleanField(default=False)


    @classmethod
    def get_moderation_type(cls,room_id)->str:
        try:
            obj=RoomModerationType.objects.annotate(
                mod_type=Case(
                    When(is_auto_moderated=True,then=Value("Auto Moderated")),
                    When(is_semi_auto_moderated=True,then=Value("Semi Auto Moderated")),
                    When(is_manually_moderated=True,then=Value("Manually Moderated")),
                )
            )
            return obj.get(room_id=room_id).mod_type
        except Exception as e:
            logger.error(e)
            return None
            