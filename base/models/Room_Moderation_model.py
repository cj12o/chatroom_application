from django.db import models
from ..logger import logger
from enum import IntEnum
class ModerationType(IntEnum):
    Auto=-2
    SemiAuto=-1
    Manual=0
class RoomModerationType(models.Model):
    room=models.OneToOneField(to="Room",on_delete=models.CASCADE,related_name="room_moderation_type")
    # is_auto_moderated=models.BooleanField(default=False)
    # is_semi_auto_moderated=models.BooleanField(default=True)
    # is_manually_moderated=models.BooleanField(default=False)
    moderation_type=models.IntegerField(
        choices=[
            (ModerationType.SemiAuto,"semi-auto moderation"),
            (ModerationType.Auto,"auto moderation"),
            (ModerationType.Manual,"manual moderation")
        ],
        default=ModerationType.SemiAuto,
    )

    @classmethod
    def get_moderation_type(cls,room_id)->int:
        "-1->semi-auto mod,-2->auto mod ,0->manual mod"
        try:
            return RoomModerationType.objects.get(room__id=room_id).moderation_type
        except Exception as e:
            logger.error(e)
            return None
            