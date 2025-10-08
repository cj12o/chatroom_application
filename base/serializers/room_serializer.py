from rest_framework import serializers
from ..models.room_model import Room
from ..models.topic_model import Topic
from django.db.models import Q
from django.contrib.auth.models import User

from.user_serializer import UserSerializer
from ..views.topic_filter import topicsList

class RoomSerializer(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    parent_topic=serializers.SerializerMethodField()  
    members=serializers.SerializerMethodField()  
    class Meta:
        model=Room
        fields='__all__'

    def get_author(self,obj):
        return obj.author.username
      
    def get_parent_topic(self,obj):
        return obj.parent_topic.topic
    
    #############
    def get_members(self,obj):
        try:
            members=Room.objects.filter(id=obj.id).values('members')
            lst=[]
            for member in members:
                id=member["members"]
                name=User.objects.get(id=id).username
            dct={'member_name':name,'memeber_id':id}
            lst.append(dct)
            print(f"name:{name} id:{id}")
        # print(f"✌️✌️members:{members}")
            print(f"😀😀lst{lst}")
            return lst
        except User.DoesNotExist:
            return []
        
class RoomSerializerForCreation(serializers.ModelSerializer):

    class Meta:
        model=Room
        fields=['name','description','topic','is_private']
    
    def create(self,validated_data):
        
        # room=Room.objects.create(author=self.context["request"])
        name=validated_data["name"]
        description=validated_data["description"]
        topic=validated_data["topic"]
        ####
        main_topic=topicsList(validated_data["topic"])
        print(f"✅✅✅main topic:{main_topic}")
        
        parent_topic=Topic.objects.get(topic=main_topic)
        ####
        is_private=False
        if "is_private" in validated_data:
            is_private=validated_data["is_private"]
        room=Room.objects.create(author=self.context["request"],name=name,description=description,topic=topic,parent_topic=parent_topic,is_private=is_private)
        room.save()
        return room
        
        
