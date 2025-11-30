from rest_framework import serializers
from ..models.message_model import Message,Vote
from django.db.models import Q
from django.conf import settings
from ..logger import logger

class MessageSerializerForCreation(serializers.Serializer):
    id=serializers.SerializerMethodField()
    author=serializers.SerializerMethodField()
    room=serializers.SerializerMethodField()
    message=serializers.SerializerMethodField()
    images_msg=serializers.SerializerMethodField()
    file_msg=serializers.SerializerMethodField()
    parent=serializers.SerializerMethodField()
    upvotes=serializers.SerializerMethodField()
    downvotes=serializers.SerializerMethodField()
    children=serializers.SerializerMethodField()
    hasPoll=serializers.SerializerMethodField()
    is_unsafe=serializers.SerializerMethodField()

 
    def get_id(self,obj):
        return obj.id

    def get_author(self,obj):
        # dct={"username":obj.author.username,"user_id":obj.author.id}
        return obj.author.username
    
    def get_message(self,obj):
        return obj.message
    
    
    def get_room(self,obj):
        return obj.room.name
    
    def get_images_msg(self,obj):
        try:
            return f"{settings.SITE_BASE_URL}{obj.images_msg.url}"
        except Exception:
            # print(f"Error in image {e}")
            return None
        
    
    def get_file_msg(self,obj):
        try:
            return f"{settings.SITE_BASE_URL}{obj.file_msg.url}"
        except Exception:
            return None
    
    def get_children(self,obj):
        # try:
        #     return [ob.id for ob in obj.parent_message.all()]
        # except Exception as e:
        return []
    def get_parent(self,obj):
        try:
            return obj.parent.id
        except Exception:
            return None
        
    def get_upvotes(self,obj):
        try:
            votes=Vote.objects.filter(Q(message__id=obj.id))
            self.context["downvotes"]=len(votes.filter(Q(vote=-1)))
            return len(votes.filter(Q(vote=1)))
        except Exception as e:
            logger.error(e)
            return 0
    
    def get_downvotes(self,obj):
        try:
            return self.context["downvotes"]
        except Exception as e:
            logger.error(e)
            return 0
    
    def get_hasPoll(self,obj):
        if obj.poll_set.exists(): 
            return True
        return False
    
    def get_is_unsafe(self,obj):
        return obj.is_unsafe

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["message", "file_msg", "images_msg", "parent"]

        extra_kwargs = {
            "message": {"allow_blank": True, "required": False},
            "file_msg": {"required": False},
            "images_msg": {"required": False},
            "parent": {"required": False},
        }

    def create(self, validated_data):
        author = self.context["author"]
        room = self.context["room"]

        return Message.objects.create(
            author=author,
            room=room,
            **validated_data
        )

    
class MessageSerializerForModeration(serializers.Serializer):
    
    id=serializers.SerializerMethodField()
    message=serializers.SerializerMethodField()
    images_msg=serializers.SerializerMethodField()
    file_msg=serializers.SerializerMethodField()

    def get_id(self,obj):
        try:
            return obj.id
        except Exception as e:
            logger.error(e)
            return None
    
    def get_message(self,obj):
        try:
            return obj.message
        except Exception as e:
            logger.error(e)
            return None
        
    def get_images_msg(self,obj):
        try:
            return f"{settings.SITE_BASE_URL}{obj.images_msg.url}"
        except Exception as e:
            logger.error(e)
            return None
        
    
    def get_file_msg(self,obj):
        try:
            return f"{settings.SITE_BASE_URL}{obj.file_msg.url}"
        except Exception as e:
            logger.error(e)
            return None