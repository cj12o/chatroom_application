from rest_framework import serializers
from ..views.logger import logger

class Room_memeber_stats_seriaizer(serializers.Serializer):
    """serilaizes
            stats
        {
            "id": 0,
            "name": "ALEX_123",
            "msg_count": 4,
            "vote_count": 0
        },
    """
    msg_count=serializers.SerializerMethodField()
    vote_count=serializers.SerializerMethodField()
    username=serializers.SerializerMethodField()
    id=serializers.SerializerMethodField()

    def get_msg_count(self,obj):
        try:    
            return obj.msg_count
        except Exception as e:
            logger.error(e)
            
    def get_vote_count(self,obj):  
        try:
            return obj.vote_count
        except Exception as e:
            logger.error(e)
            
    
    def get_username(self,obj):
        try:
            return obj.username
        except Exception as e:
            logger.error(e)
            
    def get_id(self,obj):
        try:
            return obj.id
        except Exception as e:
            logger.error(e)
            