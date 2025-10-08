from rest_framework import serializers
from ..models.userprofile_model import UserProfile
from ..models.room_model import Room
from ..models.message_model import Message

class UserProfSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields='__all__'


"""used to serialize a users created room """
class RoomsCreatedSerializer(serializers.ModelSerializer):
    class Meta:
        model=Room
        fields=['name']




