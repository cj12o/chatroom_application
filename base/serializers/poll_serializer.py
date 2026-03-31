from rest_framework import serializers
from ..models.poll_model import Poll,PollVote
from ..services.user_services import build_profile_pic_url


class PollSerializer(serializers.ModelSerializer):

    author=serializers.SerializerMethodField()
    choices=serializers.SerializerMethodField()
    class Meta:
        model=Poll
        fields="__all__"

    def get_author(self,obj):
        try:
            dct={"username":obj.author.username}
            pic_url = build_profile_pic_url(obj.author.profile)
            if pic_url:
                dct["profile_pic"] = pic_url
            return dct
        except Exception as e:
            return None

    def get_choices(self,obj):
        return obj.choices
    

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model=PollVote,
        fields="__all__"