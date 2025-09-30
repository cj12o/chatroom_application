from django.contrib import admin
from .models.user_model import UserProfile

# Register your models here.
admin.site.register(UserProfile)