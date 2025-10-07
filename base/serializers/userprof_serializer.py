from rest_framework import serializers
from ..models.userprofile_model import UserProfile
from ..models.room_model import Room
from ..models.message_model import Message

class UserProfSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields='__all__'


class RoomsCreatedSerializer(serializers.ModelSerializer):
    class Meta:
        model=Room
        fields=['name']

class RoomsParticipatedSerializer(serializers.ModelSerializer):
    class Meta:
        model=Message
        fields=['author']


