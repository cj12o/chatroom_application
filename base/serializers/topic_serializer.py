from rest_framework import serializers
from ..models.topic_model import Topic

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model=Topic
        fields='__all__'