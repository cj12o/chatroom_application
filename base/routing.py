from django.urls  import path
from  .consumers import vote_message_consumers
from .consumers.chatbot_consumer import LlmConsumer
from .consumers.notification_consumer import NotificationConsumer
websocket_urlpatterns=[
    path("ws/chat/<str:q>/",vote_message_consumers.ChatConsumer.as_asgi()),
    path("ws/chatbot/<str:q>/",LlmConsumer.as_asgi()),
    path("ws/notify/",NotificationConsumer.as_asgi())

]