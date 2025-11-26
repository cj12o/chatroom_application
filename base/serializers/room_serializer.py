from rest_framework import serializers
from ..models.room_model import Room
from ..models.topic_model import Topic
from django.db.models import Q
from django.contrib.auth.models import User
from ..models.userprofile_model import UserProfile

from.user_serializer import UserSerializer
from ..views.topic_filter import topicsList
from ..views.logger import logger
import json
from ..views.topic_filter import topicsList

class RoomSerializerForPagination(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    parent_topic=serializers.SerializerMethodField()  
    # members=serializers.SerializerMethodField()  
    isMember=serializers.SerializerMethodField()
    moderator=serializers.SerializerMethodField()
    tags=serializers.SerializerMethodField()

    class Meta:
        model=Room
        fields='__all__'

    def get_parent_topic(self,obj):
        try:
            return obj.parent_topic.topic
        except Exception as e:
            logger.error(e)

    
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
            print(f"ERROR in getting members NOT exists")
            return []
        
    def get_isMember(self,obj)->bool:
        try:
            username=self.context["username"]
            if not username:return False
            qs=obj.members.filter(Q(username=username))
            if len(qs)>0:return True
            return False
        except Exception as e:
            print(f"ERROR in getting isMember:{str(e)}")
            return False
    
    def get_moderator(self,obj):
        try:
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
        except Exception as e:
            print(f"ERROR in getting moderator:{str(e)}")
            
    
    def get_author(self,obj):
        try:
            dct={}
            dct["id"]=obj.author.id
            dct["name"]=obj.author.username
            return dct
        except Exception as e:
            print(f"ERROR in getting author:{str(e)}")

    
    def get_tags(self,obj):
        try:
            if len(obj.tags)<1:return []
            print(f"obj.tags:{obj.tags}")
            return obj.tags
        except Exception as e:
            print(f"ERROR in getting tags:{str(e)}")
    

class RoomSerializer(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    parent_topic=serializers.SerializerMethodField()  
    members=serializers.SerializerMethodField() 
    moderator=serializers.SerializerMethodField()
    tags=serializers.SerializerMethodField()

    class Meta:
        model=Room
        fields='__all__'

    def get_parent_topic(self,obj):
        return obj.parent_topic.topic
    
    def get_members(self,obj):
        try:
            members=obj.members.all()
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
    
    def get_tags(self,obj):
        if len(obj.tags)<1:return []
        return obj.tags




class RoomSerializerForCreation(serializers.ModelSerializer):
    moderator = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )

    class Meta:
        model = Room
        fields = ['name', 'description', 'topic', 'is_private', 'moderator','tags']

    def create(self, validated_data):
        moderators = validated_data.pop("moderator", [])
        user = self.context["request"].user

        main_topic = topicsList(validated_data["topic"])
        parent_topic = Topic.objects.get(topic=main_topic)

        room = Room.objects.create(
            author=user,
            **validated_data,
            parent_topic=parent_topic,
        )

        # Add moderators
        users = User.objects.filter(username__in=moderators)
        room.moderator.set(users)

        return room


    def update(self, instance, validated_data):
        try:
            for attr,v in validated_data.items():
                if attr not in ["id","moderator","topic"]:
                    setattr(instance,attr,v)
                
                if "topic" in validated_data:
                    parent_topic=topicsList(validated_data["topic"])
                    parent_topic_obj=Topic.objects.get(topic=parent_topic)
                    instance.parent_topic=parent_topic_obj
                    instance.topic=validated_data["topic"]

                if "moderator" in validated_data:
                    mods=User.objects.filter(id__in=validated_data["moderator"])
                    instance.moderator.set(mods)
            
            instance.save()
            print(f"parent_topic={instance.parent_topic.topic}")

            return instance

        except Exception as e:
            logger.error(e)
            