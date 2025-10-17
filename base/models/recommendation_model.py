
from django.db import models
from django.contrib.auth.models import User
from ..models.room_model import Room
# Task on every session closing
# del old and insert new 

class Recommend(models.Model):
    user=models.ForeignKey(to=User,on_delete=models.CASCADE)
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE)
    reason=models.CharField()
    session=models.CharField()

