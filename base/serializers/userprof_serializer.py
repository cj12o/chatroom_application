from rest_framework import serializers
from ..models.userprofile_model import UserProfile
from ..models.room_model import Room
from ..models.message_model import Message,User
from django.conf import settings
from ..logger import logger

# class UserProfSerializer(serializers.ModelSerializer):
#     profile_pic=serializers.SerializerMethodField()
#     class Meta:
#         model=UserProfile
#         fields='__all__'

#     def get_profile_pic(self,obj):
#         if obj.profile_pic:
#             return f"{settings.SITE_BASE_URL}{obj.profile_pic.url}"
#         return None


class UserProfSerializer(serializers.ModelSerializer):
    profile_pic=serializers.SerializerMethodField()

    class Meta:
        model=UserProfile
        fields='__all__'

    def get_profile_pic(self,obj):
        if obj.profile_pic:
            return f"{settings.SITE_BASE_URL}{obj.profile_pic.url}"
        return None

    def create(self, validated_data):
        #calls just normal create from parent class
        return UserProfile.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        try:
            user_db_instance=User.objects.get(username=self.context["request"].user.username)
            for attr,v in validated_data.items():
                setattr(instance,attr,v)
                
            
            if "profile_pic" in self.context["request"].FILES:
                img=self.context['request'].FILES.get('profile_pic')
                instance.profile_pic=img 

            if "email_id" in self.context["request"].data:
                user_db_instance.email=self.context["request"].data.get("email_id") 
                

            if "username" in self.context["request"].data:
                user_db_instance.username=self.context["request"].data.get("username") 
                
            if "delete_profile_pic" in self.context["request"].data:
                if self.context["request"].data.get("delete_profile_pic").lower()=="true":
                    instance.profile_pic=None
                    
            user_db_instance.save()
            instance.save()       
            return instance
        except Exception as e:
            logger.error(e)



"""used to serialize a users created room """
class RoomsCreatedSerializer(serializers.ModelSerializer):
    class Meta:
        model=Room
        fields=['name','id']




