from django.db import models
from .room_model import Room
from django.contrib.auth.models import User 

class Message(models.Model):
    room = models.ForeignKey(to=Room,on_delete=models.CASCADE,related_name="room_message")
    author=models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="author_message")
    message = models.TextField(null=False,blank=False)
    images_msg=models.ImageField(null=True,upload_to="images/")
    file_msg=models.FileField(null=True,upload_to="files/")
    parent=models.ForeignKey(to="self",on_delete=models.CASCADE,null=True,related_name="parent_message")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Vote(models.Model):
    user=models.ForeignKey(to=User,on_delete=models.CASCADE)
    message=models.ForeignKey(to=Message,on_delete=models.CASCADE)
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE)
    vote=models.SmallIntegerField(choices=[(1,"upvote"),(-1,"downvote")])

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['user', 'message','room'], name='unique_user_message_room_vote')
        ]