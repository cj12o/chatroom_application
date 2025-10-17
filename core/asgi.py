"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter,URLRouter
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from base.middlewares.channel_auth_middleware import TokenAuthChannelMiddleware


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


django_asgi_app = get_asgi_application()

from base import routing


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # Just HTTP for now. (We can add other protocols later.)

    "websocket":AllowedHostsOriginValidator(
        TokenAuthChannelMiddleware( AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns)))
    )
})