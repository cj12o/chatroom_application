from rest_framework import serializers
from ..models.room_model import Room

from.user_serializer import UserSerializer


class RoomSerializer(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    class Meta:
        model=Room
        fields='__all__'

    def get_author(self,obj):
        return obj.author.username
      

class RoomSerializerForCreation(serializers.ModelSerializer):
    class Meta:
        model=Room
        fields=['name','description','topic','is_private']
    
    def create(self,validated_data):
        room=Room.objects.create(author=self.context["request"])
        room.name=validated_data["name"]
        room.description=validated_data["description"]
        room.topic=validated_data["topic"]
        if "is_private" in validated_data:
            room.is_private=validated_data["is_private"]
        
        room.save()
        return room
        
