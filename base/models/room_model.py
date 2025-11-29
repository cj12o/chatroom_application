from django.db import models
from django.contrib.auth.models import User
from .topic_model import Topic

class Room(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name="author_rooms")
    name=models.CharField(max_length=100,unique=True)
    description=models.TextField()
    parent_topic=models.ForeignKey(Topic,related_name="room_topic",on_delete=models.CASCADE)
    topic=models.CharField(max_length=100)
    is_private=models.BooleanField(null=False,blank=False,default=False)
    members=models.ManyToManyField(to=User,related_name="room_member")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    tags=models.JSONField(default=dict)
    moderator=models.ManyToManyField(to=User,related_name="room_moderator",default=None)
    
    def __str__(self) -> str:
        return self.name





    
    
    
    