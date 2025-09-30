from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


"""
for last seen we will use middleware
at every request that middleware updates last seen
"""


"""
upload_to='avatars/' → uploaded images are saved under:
MEDIA_ROOT/avatars/"""

class UserProfile(models.Model):
    username=models.CharField(null=False,blank=False,max_length=100)
    email=models.EmailField(null=False,blank=False)
    bio=models.TextField(null=True,blank=True)
    last_seen=models.DateTimeField(default=timezone.now())
    is_online=models.BooleanField(default=False)
    profile_pic=models.ImageField(null=True,blank=True,upload_to='avatars/')
    roles=models.CharField(max_length=10,choices=[("admin","Admin"),("User","user"),("Moderator","moderator")])
    created_at=models.DateField(auto_now_add=True)


