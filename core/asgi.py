# """
# ASGI config for core project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
# """

# import os
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# django.setup()



# from channels.routing import ProtocolTypeRouter,URLRouter
# from django.core.asgi import get_asgi_application
# from channels.security.websocket import AllowedHostsOriginValidator
# from base.middlewares.channel_auth_middleware import TokenAuthChannelMiddleware


# django_asgi_app = get_asgi_application()

# from base import routing


# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     # Just HTTP for now. (We can add other protocols later.)

#     "websocket":AllowedHostsOriginValidator(
#         TokenAuthChannelMiddleware((URLRouter(routing.websocket_urlpatterns)))
#     )
# })


import os
import django
import time

print("STEP 1: Starting ASGI load", flush=True)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

print("STEP 2: Environment set", flush=True)

start = time.time()
django.setup()
print(f"STEP 3: django.setup() done in {time.time() - start:.2f}s", flush=True)


print("STEP 4: Importing ASGI components", flush=True)
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator

print("STEP 5: Importing custom middleware", flush=True)
from base.middlewares.channel_auth_middleware import TokenAuthChannelMiddleware

print("STEP 6: Creating Django ASGI app", flush=True)
django_asgi_app = get_asgi_application()

print("STEP 7: Importing routing", flush=True)
from base import routing

print("STEP 8: Building ProtocolTypeRouter", flush=True)

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": AllowedHostsOriginValidator(
        TokenAuthChannelMiddleware(
            URLRouter(routing.websocket_urlpatterns)
        )
    )
})

print("STEP 9: ASGI application ready ✅", flush=True)