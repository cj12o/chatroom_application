from django.contrib import admin
from .models.user_model import UserProfile
from .models.room_model import Room

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Room)

