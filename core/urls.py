from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/",include('base.api.urls')),
    path("api/room_stats/",include('base.api.room_stats_urls')),
    path("api/moderation/",include('base.api.room_moderation_urls'))
]

if settings.DEBUG==True:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)