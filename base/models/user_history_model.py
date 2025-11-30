from django.db import models
from django.contrib.auth.models import User

class History(models.Model):
    user=models.ForeignKey(to=User,on_delete=models.CASCADE)
    session=models.CharField(max_length=100,unique=True,default="NAN")  #from redux
    created_at=models.DateTimeField(auto_now_add=True)
    hist=models.JSONField(null=True,blank=True)

    



   