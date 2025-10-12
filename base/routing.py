from django.urls  import path
from .consumers import ChatConsumer

websocket_urlpatterns=[
    path("ws/chat/<str:q>/",ChatConsumer.as_asgi())
]