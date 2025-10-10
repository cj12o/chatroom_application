from django.db import models
from django.contrib.auth.models import User
from .room_model import Room

class History(models.Model):
    user=models.ForeignKey(to=User,on_delete=models.CASCADE)
    session=models.CharField(max_length=100,null=True,blank=True)  #from redux
    rooms_visited=models.ForeignKey(to=Room,on_delete=models.CASCADE,related_name="room_history") #room_id
    time_spent=models.IntegerField(null=False,blank=False,default=0)
    created_at=models.DateTimeField(auto_now_add=True)



   