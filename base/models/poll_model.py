from django.db import models
from django.contrib.auth.models import User 

from .room_model import Room
from .message_model import Message

class Poll(models.Model):
    message=models.ForeignKey(to=Message,on_delete=models.CASCADE)
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE)
    author=models.ForeignKey(to=User,on_delete=models.CASCADE)
    question=models.TextField()
    choices=models.JSONField(default=dict)
    created_at=models.DateTimeField(auto_now_add=True)


class PollVote(models.Model):
    poll=models.ForeignKey(to=Poll,on_delete=models.CASCADE,related_name="message_polls")
    user=models.ForeignKey(to=User,on_delete=models.CASCADE)
    choiceSelected=models.IntegerField(null=False,blank=False,default=1)
    created_at=models.DateTimeField(auto_now_add=True)

    

