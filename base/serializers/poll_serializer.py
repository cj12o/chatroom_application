from rest_framework import serializers
from ..models.poll_model import Poll



class PollSerializer(serializers.ModelSerializer):
    
    author=serializers.SerializerMethodField()
    choices=serializers.SerializerMethodField()
    class Meta:
        model=Poll
        fields="__all__"
    
    def get_author(self,obj):
        return obj.author.username
    
    def get_choices(self,obj):
        return obj.choices["choices"]
    