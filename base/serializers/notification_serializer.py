from rest_framework import serializers

class PersonalNotificationSerializer(serializers.Serializer):
    room_id=serializers.SerializerMethodField()
    notify=serializers.SerializerMethodField()
    
    def get_notify(self,obj):
        return obj.notification.notify
    
    def get_room_id(self,obj):
        return obj.notification.room.id

    
