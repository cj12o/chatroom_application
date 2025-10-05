from rest_framework import serializers
from ..models.userprofile_model import UserProfile


class UserProfSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields='__all__'
    
        