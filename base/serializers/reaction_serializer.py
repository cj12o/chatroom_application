# from  rest_framework import serializers
# import regex

# from ..models.message_model import Reaction,Emoji

# class ReactionSerializer(serializers.ModelSerializer):

#     class Meta:
#         model=Reaction
#         fields=["reaction"] 
    
#     def validate(self,data):
#         if "reaction" not in data:
#             raise serializers.ValidationError("Reaction is required")
#         return data
    

#     def create(self,validated_data):
#         user=self.context["user"]
#         msg=self.context["msg"]
        
#         reaction=Reaction.objects.create(author=user,message=msg)
#         reaction.reaction=validated_data["reaction"]
#         reaction.save()
#         return reaction

    
# class EmojiSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Emoji
#         fields=["emoji"] 

#     def validate(self,data):
#         if "emoji" not in data:
#             raise serializers.ValidationError("Emoji is required is required")
        
#         emoji_pattern = regex.compile(r'[\p{Emoji}]')
#         for ch in data["emoji"]:
#             if not emoji_pattern.fullmatch(ch):
#                 raise serializers.ValidationError("Only emoji characters are allowed.")
        
#         return data
    

#     def create(self,validated_data):
#         user=self.context["user"]
#         msg=self.context["msg"]
        
#         emoji=Emoji.objects.create(author=user,message=msg)
#         emoji.emoji=validated_data["emoji"]
#         emoji.save()
#         return emoji
    