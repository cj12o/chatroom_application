from django.urls  import path
from  .consumers import vote_message_consumers
from .consumers.chatbot_consumer import LlmConsumer
websocket_urlpatterns=[
    path("ws/chat/<str:q>/",vote_message_consumers.ChatConsumer.as_asgi()),
    path("ws/chatbot/",LlmConsumer.as_asgi())
]