from django.db import models
from django.contrib.auth.models import User

class History(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    rooms_visited=models.JSONField(null=True,blank=False) #room_id
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username