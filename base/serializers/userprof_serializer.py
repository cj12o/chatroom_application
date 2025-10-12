from rest_framework import serializers
from ..models.userprofile_model import UserProfile
from ..models.room_model import Room
from ..models.message_model import Message

class UserProfSerializer(serializers.ModelSerializer):
    profile_pic=serializers.SerializerMethodField()
    class Meta:
        model=UserProfile
        fields='__all__'

    def get_profile_pic(self,obj):
        if obj.profile_pic:
            return "http://127.0.0.1:8000"+obj.profile_pic.url
        return None



"""used to serialize a users created room """
class RoomsCreatedSerializer(serializers.ModelSerializer):
    class Meta:
        model=Room
        fields=['name','id']




