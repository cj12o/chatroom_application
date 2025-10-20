from django.contrib import admin
from .models.userprofile_model import UserProfile
from .models.room_model import Room
from .models.message_model import Message,Vote
from .models.topic_model import Topic
from .models.user_history_model import History
from .models.recommendation_model import Recommend

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Topic)
admin.site.register(History)
admin.site.register(Recommend)
admin.site.register(Vote)
