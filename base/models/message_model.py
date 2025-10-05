from django.db import models
from .room_model import Room
from django.contrib.auth.models import User 

class Message(models.Model):
    room = models.ForeignKey(to=Room,on_delete=models.CASCADE,related_name="room_msg")
    author=models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="author_msg")
    message = models.TextField(null=False,blank=False)
    reactions = models. ManyToManyField(to=User,through='Reaction')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Reaction(models.Model):
    author=models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="author_reaction")
    message=models.ForeignKey(to=Message,on_delete=models.CASCADE)
    emoji=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Emoji(models.Model):
    author=models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="author_emoji")
    message=models.ForeignKey(to=Message,on_delete=models.CASCADE,related_name="message_emoji")
    emoji=models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

