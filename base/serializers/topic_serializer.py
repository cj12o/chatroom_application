from rest_framework import serializers
from ..models.topic_model import Topic
from ..logger import logger

class TopicSerializer(serializers.ModelSerializer):
    
    relatedRooms=serializers.SerializerMethodField()
    
    class Meta:
        model=Topic
        fields='__all__'
    
    def get_relatedRooms(self,obj):
        try:    
            return obj.room_topic.count()
        except Exception as e:
            logger.error(e)
            return 0