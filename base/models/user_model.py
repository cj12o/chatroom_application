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
    # username
    # email
    user=models.OneToOneField(to=User,on_delete=models.CASCADE,related_name="profile",null=True)
    bio=models.TextField(null=True,blank=True)
    last_seen=models.DateTimeField(default=timezone.now)
    is_online=models.BooleanField(default=False)
    profile_pic=models.ImageField(null=True,blank=True,upload_to='avatars/')
    roles=models.CharField(max_length=10,choices=[("admin","admin"),("user","user"),("moderator","moderator")],default="user")
    created_at=models.DateField(auto_now_add=True)


