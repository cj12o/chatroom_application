from rest_framework import serializers
from ..models.notification_model import Notification

class NotificationSerializer(serializers.ModelSerializer):
    notify=serializers.SerializerMethodField()
    room=serializers.SerializerMethodField()
    
    class Meta:
        model=Notification
        fields="__all__"
    
    def get_notify(self,obj):
        return obj.notify
    
    def get_room(self,obj):
        return {"room_id":obj.room.id,"room_name":obj.room.name}