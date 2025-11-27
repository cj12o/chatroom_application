from rest_framework import serializers
from ..models.recommendation_model import Recommend
from ..models.room_model import Room
from ..models.userprofile_model import UserProfile

class RecommndationSerializer(serializers.Serializer):
    id=serializers.SerializerMethodField()
    author=serializers.SerializerMethodField()
    parent_topic=serializers.SerializerMethodField()
    members=serializers.SerializerMethodField()  
    moderator=serializers.SerializerMethodField()
    name=serializers.SerializerMethodField()
    description=serializers.SerializerMethodField()
    tags=serializers.SerializerMethodField()
    topic=serializers.SerializerMethodField()
    reason=serializers.CharField()
    is_private=serializers.SerializerMethodField()
    created_at=serializers.SerializerMethodField()
    updated_at=serializers.SerializerMethodField()
    
    class Meta:
        model=Recommend
        fields="__all__"

    def get_id(self,obj):
        return obj.room.id


    def get_author(self,obj):
        dct={}
        dct["id"]=obj.room.author.id
        dct["name"]=obj.room.author.username
        return dct
    
    def get_parent_topic(self,obj):
        return obj.room.parent_topic.topic
 
    def get_members(self,obj):
        room=Room.objects.get(name=obj.room.name)
        members=room.members.all()
        lst=[]
        for member in members:
            dct={}
            dct["member_id"]=member.id
            dct["member_name"]=member.username
            dct["status"]=member.profile.is_online
            lst.append(dct)
        return lst
    
    def get_moderator(self,obj):
        room=Room.objects.get(name=obj.room.name)
        mods=room.moderator.all()
        lst=[]
        for mod in mods:
            dct={}
            dct["id"]=mod.id
            dct["status"]=UserProfile.objects.get(id=mod.id).is_online
            dct["username"]=mod.username
            lst.append(dct)
        return lst
 
    def get_name(self,obj):
        return obj.room.name

    def get_description(self,obj):
        return obj.room.name
    
    def get_topic(self,obj):
        return obj.room.topic
    
    def get_is_private(self,obj):
        return obj.room.is_private
    
    def get_created_at(self,obj):
        return obj.room.created_at
    
    def get_updated_at(self,obj):
        return obj.room.updated_at
        
    def get_tags(self,obj):
        return obj.room.tags
