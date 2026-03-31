from rest_framework import serializers
from ..models.join_request_model import JoinRequest
from ..models.userprofile_model import User
from ..services.user_services import build_profile_pic_url

class JoinRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()
    user_profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = JoinRequest
        fields = ['id', 'user', 'room', 'status', 'created_at', 'user_name', 'room_name', 'user_profile_pic']
        read_only_fields = ['status', 'created_at']

    def get_user_name(self, obj):
        return obj.user.username

    def get_room_name(self, obj):
        return obj.room.name
    
    def get_user_profile_pic(self, obj):
        if hasattr(obj.user, 'profile'):
            return build_profile_pic_url(obj.user.profile)
        return None
