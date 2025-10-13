from rest_framework import serializers
from ..models.room_model import Room
from ..models.topic_model import Topic
from django.db.models import Q
from django.contrib.auth.models import User
from ..models.userprofile_model import UserProfile

from.user_serializer import UserSerializer
from ..views.topic_filter import topicsList

class RoomSerializer(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    parent_topic=serializers.SerializerMethodField()  
    members=serializers.SerializerMethodField()  
    moderator=serializers.SerializerMethodField()
    class Meta:
        model=Room
        fields='__all__'

    def get_parent_topic(self,obj):
        return obj.parent_topic.topic
    
    #############
    def get_members(self,obj):
        try:
            room=Room.objects.get(id=obj.id)
            members=room.members.all()
            lst=[]
            for member in members:
                dct={}
                dct["member_id"]=member.id
                dct["member_name"]=member.username
                dct["status"]=member.profile.is_online
                lst.append(dct)

            # print(f"😀😀lst{lst}")
            return lst
        except User.DoesNotExist:
            return []
        
    def get_moderator(self,obj):
        lst=[]
        room=Room.objects.get(id=obj.id)
        mods=room.moderator.all()
        for mod in mods:
            dct={}
            dct["id"]=mod.id
            dct["status"]=UserProfile.objects.get(id=mod.id).is_online
            dct["username"]=mod.username
            lst.append(dct)
        return lst
    
    def get_author(self,obj):
        dct={}
        dct["id"]=obj.author.id
        dct["name"]=obj.author.username
        return dct
        
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

        # if "moderator" in validated_data:
        #     for moderator in validated_data["moderator"]:
        #         print(f"-----------MOD name:{moderator}")
        #         mod=User.objects.get(username=moderator)
        #         room.moderator.add(mod)
        # else:
        #     room.moderator.add(self.context["request"])
        return room
        
        
