from  rest_framework import serializers
from ..models  import History


class HistorySerializer(serializers.Serializer):
    session=serializers.CharField()
    time_spent=serializers.IntegerField()
   
   
    def validate(self,data):
        if "session" not in data:
            raise serializers.ValidationError("Session is required")
        elif "time_spent" not in data:
            raise serializers.ValidationError("Time Spent is required")
        return data

    def create(self,validated_data):
        user=self.context["user"]
        room=self.context["room"]
        history=History.objects.create(user=user,rooms_visited=room)
        history.session=validated_data["session"]
        history.time_spent=validated_data["time_spent"]
        history.save()
        return history
