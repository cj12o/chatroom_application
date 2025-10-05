from django.contrib import admin
from .models.userprofile_model import UserProfile
from .models.room_model import Room
from .models.message_model import Message,Reaction
from .models.topic_model import Topic

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Reaction)
admin.site.register(Topic)