from rest_framework import serializers


from ..models.user_model import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username','email']

    def validate(self,validated_data):
        users=User.objects.all()
        if  users:
            if users.filter(email=validated_data["email"]):
                raise serializers.ValidationError("User with this email is already registered")
            
            elif users.filter(username=validated_data["username"]):
                raise serializers.ValidationError("Username is already registered")
        
        return validated_data 
        
    