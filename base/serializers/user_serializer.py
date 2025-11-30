from rest_framework import serializers
from django.db.models import Q

from django.contrib.auth.models import User
from ..models.userprofile_model import UserProfile
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

        if not self.partial:
            if users.filter(email=validated_data["email"]).exists():
                raise serializers.ValidationError("User with this email is already registered")
            
            if users.filter(username=validated_data["username"]).exists():
                raise serializers.ValidationError("Username is already registered")    

        if self.partial:
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
    email=serializers.EmailField()
    password=serializers.CharField()
   

    def validate(self,validated_data):
        # print(f"Validated data=>{validated_data}")
        try:
            email=validated_data["email"]
            password=validated_data["password"]
            user=User.objects.get(Q(email=email))
        
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid user")
        

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password")

        
        return validated_data
    


class SignupSerializer(serializers.Serializer):
    username=serializers.CharField()
    email=serializers.EmailField()
    password=serializers.CharField()
    # class Meta:
    #     model=User
    #     fields=["username","password","email"]

    #wriiting custom validation 
    def validate(self,data):
        print(f"data=>{data}")
        if "username" not in data.keys():
            raise serializers.ValidationError("username is required")
        elif "email" not in data:
            raise serializers.ValidationError("email is required")
        elif "password" not in data:
            raise serializers.ValidationError("password is required")
    
        
        
        user=User.objects.filter(Q(username=data["username"]) | Q(email=data["email"]))
        if not user:
            return data
        raise serializers.ValidationError("username or email are already Taken")
                

    def create(self,validated_data):
        user=User.objects.create(username=validated_data["username"],email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()

        #by def user profile creation
        UserProfile.objects.create(user=user)
        
        return user




