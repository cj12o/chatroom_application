from rest_framework import serializers
from ..models.join_request_model import JoinRequest
from ..models.userprofile_model import User

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
        if hasattr(obj.user, 'profile') and obj.user.profile.profile_pic:
            from django.conf import settings
            return f"{settings.SITE_BASE_URL}{obj.user.profile.profile_pic.url}"
        return None
