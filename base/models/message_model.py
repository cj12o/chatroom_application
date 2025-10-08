from django.db import models
from .room_model import Room
from django.contrib.auth.models import User 

class Message(models.Model):
    room = models.ForeignKey(to=Room,on_delete=models.CASCADE,related_name="room_message")
    author=models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="author_message")
    message = models.TextField(null=False,blank=False)
    reactions = models. ManyToManyField(to=User,through='Reaction')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent=models.ForeignKey(to="self",on_delete=models.CASCADE,null=True,related_name="parent_message")

class Reaction(models.Model):
    author=models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="author_reaction")
    message=models.ForeignKey(to=Message,on_delete=models.CASCADE,related_name="message_reaction")
    emoji=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Vote(models.Model):

    user= models.ForeignKey(User, on_delete=models.CASCADE,related_name="user_vote")
    parent_message=models.ForeignKey(to=Message,on_delete=models.CASCADE)
    vote=models.SmallIntegerField(default=0,choices=[(1, "Upvote"), (-1, "Downvote")])
    
    class Meta:
        unique_together=("user","parent_message")
