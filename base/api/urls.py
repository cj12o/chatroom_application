from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from ..views import user_views as uv


urlpatterns=[
    path("login/",uv.UserApiview.as_view()),
]

if settings.DEBUG==True:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

