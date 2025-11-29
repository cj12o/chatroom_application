from django.contrib import admin
from .models import UserProfile,Room,Message,Vote,Topic,History,Recommend,Poll,PollVote,ChatFileLog,MessageSummerizedStatus,Notification,VectorDbAdditionStatus,RoomModerationType
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Topic)
admin.site.register(History)
admin.site.register(Recommend)
admin.site.register(Vote)
admin.site.register(PollVote)
admin.site.register(Poll)
admin.site.register(ChatFileLog)
admin.site.register(MessageSummerizedStatus)
admin.site.register(Notification)
admin.site.register(VectorDbAdditionStatus)
admin.site.register(RoomModerationType)