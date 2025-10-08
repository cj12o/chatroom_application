from rest_framework import serializers
from ..models.message_model import Message,Reaction



class MessageSerializerForCreation(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    room=serializers.SerializerMethodField()
    # reactions=serializers.SerializerMethodField()

    class Meta:
        model=Message
        fields='__all__'

    def get_author(self,obj):
        return obj.author.username
    
    def get_room(self,obj):
        return obj.room.name
    
    # def get_reactions(self,obj):
    #     reactions=reactions=obj.message_reaction.all
    #     return [
    #         {
    #             "id": r.id,
    #             "author": r.author.username,
    #             "emoji": r.emoji,
    #             "created_at": r.created_at,
    #         }
    #         for r in reactions
    #     ]

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