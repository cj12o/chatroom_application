from rest_framework import serializers
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.models import User
from ..models import UserProfile,RoomModerationType,Room,Topic
from ..models.join_request_model import JoinRequest, RequestStatus

from ..views.topic_filter import topicsList
from ..logger import logger
from ..models.Room_Moderation_model import ModerationType
from django.conf import settings
import os


class RoomSerializerForPagination(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    parent_topic=serializers.SerializerMethodField()  
    members=serializers.SerializerMethodField()  
    isMember=serializers.SerializerMethodField()
    moderator=serializers.SerializerMethodField()
    tags=serializers.SerializerMethodField()
    moderation_type=serializers.SerializerMethodField()
    has_pending_request=serializers.SerializerMethodField()

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
                dct["profile_image"]=f"{settings.SITE_BASE_URL}{member.profile.profile_pic.url}" if member.profile.profile_pic else None
                lst.append(dct)

            print(f"😀😀lst{lst}")
            return lst
        except User.DoesNotExist:
            logger.error("ERROR in getting members NOT exists")
            return []
        
    def get_isMember(self,obj)->bool:
        try:
            user_auth_status=self.context["user_auth_status"]
            if not user_auth_status:
                return False
            qs=obj.members.filter(Q(username=self.context["username"]))
            if len(qs)>0:
                return True
            return False
        except Exception as e:
            logger.error(e)
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
            if len(obj.tags)<1:
                return []
            print(f"obj.tags:{obj.tags}")
            return obj.tags
        except Exception as e:
            print(f"ERROR in getting tags:{str(e)}")
    
    def get_moderation_type(self,obj):
        try:    
            return RoomModerationType.get_moderation_type(obj.id)
        except Exception as e:
            logger.error(f"ERROR in getting moderation type:{str(e)}")
            return -2

    def get_has_pending_request(self,obj):
        try:
            if "request" in self.context:
                user = self.context["request"].user
                if user.is_authenticated:
                    return JoinRequest.objects.filter(user=user, room=obj, status=RequestStatus.PENDING).exists()
            elif "user_auth_status" in self.context and self.context["user_auth_status"]:
                 user = User.objects.get(username=self.context["username"])
                 return JoinRequest.objects.filter(user=user, room=obj, status=RequestStatus.PENDING).exists()
            return False
        except Exception as e:
            logger.error(f"ERROR in getting pending request:{str(e)}")
            return False
    

class RoomSerializer(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    parent_topic=serializers.SerializerMethodField()  
    members=serializers.SerializerMethodField() 
    moderator=serializers.SerializerMethodField()
    tags=serializers.SerializerMethodField()
    moderation_type=serializers.SerializerMethodField()
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
                dct["profile_image"]=f"{settings.SITE_BASE_URL}{member.profile.profile_pic.url}" if member.profile.profile_pic else None
                lst.append(dct)

            return lst
        except User.DoesNotExist:
            return []
    
    def get_moderator(self,obj):
        lst=[]
        room=Room.objects.get(id=obj.id)
        if not room.moderator.exists():
            return lst
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
        if len(obj.tags)<1:
            return []
        return obj.tags

    def get_moderation_type(self,obj):
        return RoomModerationType.get_moderation_type(obj.id)



class RoomSerializerForCreation(serializers.ModelSerializer):
    #if moderator:<=0 its users if -1 semi mod,-2 auto mod
    moderator = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Room
        fields = ['name', 'description', 'topic', 'is_private', 'moderator','tags']

    def create(self, validated_data):
        try:
            moderators = validated_data.pop("moderator", [])
            #if semi mod [-1,..ids]
            print(f"Moderators:{moderators}")
            user = self.context["request"].user

            main_topic = topicsList(validated_data["topic"])
            parent_topic = Topic.objects.get(topic=main_topic)

            with transaction.atomic():
                room = Room.objects.create(
                    author=user,
                    **validated_data,
                    parent_topic=parent_topic,
                )

                # Add moderators
                if moderators[0]<0:
                    "case when not manual moderation"
                    if moderators[0]==-1:
                        print("✅✅case when semi mod",moderators)
                        RoomModerationType.objects.create(room=room,moderation_type=ModerationType.SemiAuto)
                        moderators.pop(0)
                        users = User.objects.filter(id__in=moderators)
                        room.moderator.set(users)
                    elif moderators[0]==-2:
                        RoomModerationType.objects.create(room=room,moderation_type=ModerationType.Auto)
                
                else:    
                    "case when manual moderation"
                    RoomModerationType.objects.create(room=room,moderation_type=ModerationType.Manual)
                    users = User.objects.filter(id__in=moderators)
                    room.moderator.set(users)

                    "make owner memeber"
                    room.members.add(user)
                    room.save()

            return room

        except Exception as e:
            print("ERROR in creating room")
            logger.error(e)

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
                    if validated_data["moderator"][0]<0:
                        "case when not manual moderation"
                        instance.moderator.clear()
                        if validated_data["moderator"][0]==-1:
                            RoomModerationType.objects.update_or_create(room=instance,defaults={'moderation_type':ModerationType.SemiAuto})
                            mods=User.objects.filter(id__in=validated_data["moderator"][1:])
                            instance.moderator.set(mods)
                        elif validated_data["moderator"][0]==-2:
                            RoomModerationType.objects.update_or_create(room=instance,defaults={'moderation_type': ModerationType.Auto})
                    else:
                        RoomModerationType.objects.update_or_create(room=instance, defaults={'moderation_type': ModerationType.Manual})
                        mods=User.objects.filter(id__in=validated_data["moderator"])
                        instance.moderator.set(mods)
            
            instance.save()
            print(f"parent_topic={instance.parent_topic.topic}")

            return instance

        except Exception as e:
            logger.error(e)
            
class RoomSerializerForModeration(serializers.ModelSerializer):
    class Meta:
        model=Room
        fields=['id','name']