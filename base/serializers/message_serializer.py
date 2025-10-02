from rest_framework import serializers
from ..models.message_model import Message



class MessageSerializerForCreation(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    room=serializers.SerializerMethodField()
    class Meta:
        model=Message
        fields='__all__'

    def get_author(self,obj):
        return obj.author.username
    
    def get_room(self,obj):
        return obj.room.name


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Message
        fields=['message']

    def create(self,validated_data):
        user=self.context["request"]["user"]#user instance
        room=self.context["request"]["room"]
        msg=Message.objects.create(author=user,room=room)
        msg.message=validated_data["message"]
        msg.save()
        return msg