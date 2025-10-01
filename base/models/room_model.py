from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    # rel with user
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=100,unique=True)
    description=models.TextField()
    topic=models.CharField(max_length=100)
    is_private=models.BooleanField(null=False,blank=False,default=False)
    participants=models.ManyToManyRel(to=User,field=id,related_name="rooms")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)