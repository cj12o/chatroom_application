from django.db import models
from django.contrib.auth.models import User
from .topic_model import Topic

class Room(models.Model):
    # rel with user
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=100,unique=True)
    description=models.TextField()

    ###add
    parent_topic=models.ForeignKey(Topic,on_delete=models.CASCADE)

    ####
    topic=models.CharField(max_length=100)
    is_private=models.BooleanField(null=False,blank=False,default=False)
    participants=models.ManyToManyField(to=User,related_name="room_participant",null=True,blank=True)
    members=models.ManyToManyField(to=User,null=True,blank=True,related_name="room_member")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)