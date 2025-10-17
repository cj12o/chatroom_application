from rest_framework import serializers
from ..models.message_model import Message



class MessageSerializerForCreation(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    room=serializers.SerializerMethodField()
    images_msg=serializers.SerializerMethodField()
    file_msg=serializers.SerializerMethodField()
    # reactions=serializers.SerializerMethodField()

    class Meta:
        model=Message
        fields='__all__'

    def get_author(self,obj):
        dct={"username":obj.author.username,"id":obj.author.id}
        return dct
    
    def get_room(self,obj):
        return obj.room.name
    
    def get_images_msg(self,obj):
        try:
            return "http://127.0.0.1:8000"+obj.images_msg.url
        except Exception as e:
            pass
        finally:
            return None
    
    def get_file_msg(self,obj):
        try:
            return "http://127.0.0.1:8000"+obj.file_msg.url
        except Exception as e:
            pass
        finally:
            return None
    

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Message
        fields=['message']

    def create(self,validated_data):
        author=self.context["request"]["author"]#user instance
        room=self.context["request"]["room"]
        msg=None
        if "parent" in self.context["request"]:
            parent=self.context["request"]["parent"]
            msg=Message.objects.create(author=author,room=room,parent=parent)
            print(f"✅✅msg:{msg}")
        else:
            msg=Message.objects.create(author=author,room=room)
        
        msg.message=validated_data["message"]
        msg.save()
        return msg