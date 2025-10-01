from rest_framework import serializers
from django.db.models import Q

from django.contrib.auth.models import User

# Notes :we only write validate for post

class UserSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    username=serializers.CharField()
    email=serializers.EmailField()
    password=serializers.CharField()

    def validate(self,validated_data):
        
        users=User.objects.all()

        if self.instance:
            users=User.objects.exclude(id=self.instance.id)

        if self.partial==False:
            if users.filter(email=validated_data["email"]).exists():
                raise serializers.ValidationError("User with this email is already registered")
            
            if users.filter(username=validated_data["username"]).exists():
                raise serializers.ValidationError("Username is already registered")    

        if self.partial==True:
            if "email" in  validated_data and users.filter(email=validated_data["email"]).exists():
                raise serializers.ValidationError("User with this email is already registered")
            
            if "username" in validated_data and users.filter(username=validated_data["username"]).exists():
                raise serializers.ValidationError("Username is already registered")          

        return validated_data
    
    def create(self,validated_data):
        user=User.objects.create(username=validated_data["username"],
                            email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self,instance,validated_data):
        
        for k,v in validated_data.items():
            setattr(instance,k,v)
        
        instance.save()
        return instance
    
        

class AdminLoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField()

    def validate(self,validated_data):
        # print(f"Validated data=>{validated_data}")
        try:
            username=validated_data["username"]
            password=validated_data["password"]
            user=User.objects.get(Q(username=username)& Q(is_superuser=True))
        
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials No such Admin")
        

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password")

        return validated_data
    


