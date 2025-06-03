from django.urls import path
from . import consumers  # ChatConsumer має бути тут же

websocket_urlpatterns = [
    path("ws/chat/", consumers.ChatConsumer.as_asgi()),
]
