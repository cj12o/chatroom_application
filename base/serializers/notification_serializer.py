from rest_framework import serializers
from ..models import Notification,PersonalNotification

class PersonalNotificationSerializer(serializers.Serializer):
    notify=serializers.SerializerMethodField()
    room=serializers.SerializerMethodField()
    sent_status=serializers.BooleanField()
    mark_read_status=serializers.BooleanField()
    # class Meta:
    #     model=Notification
    #     fields="__all__"
    
    def get_notify(self,obj):
        return obj.notification.notify
    
    def get_room(self,obj):
        temp_room_obj=obj.notification.room
        return {"room_id":temp_room_obj.id,"room_name":temp_room_obj.name}
    
    def get_sent_status(self,obj):
        return obj.sent_status
    
    def get_mark_read_status(self,obj):
        return obj.mark_read
    
