from rest_framework import serializers
from ..models.poll_model import Poll,PollVote
from django.conf import settings


class PollSerializer(serializers.ModelSerializer):
    
    author=serializers.SerializerMethodField()
    choices=serializers.SerializerMethodField()
    class Meta:
        model=Poll
        fields="__all__"
    
    def get_author(self,obj):
        try:
            dct={"username":obj.author.username}
            if obj.author.profile.profile_pic:
                dct["profile_pic"]=f"{settings.SITE_BASE_URL}{obj.author.profile.profile_pic.url}"
            return dct
        except Exception as e:
            return None

    def get_choices(self,obj):
        return obj.choices
    

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model=PollVote,
        fields="__all__"