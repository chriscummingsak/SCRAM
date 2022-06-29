"""
ASGI config for SCRAM project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/

"""
import os
import sys
from pathlib import Path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from . import routing as scram_routing

# This allows easy placement of apps within the interior
# scram directory.
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(ROOT_DIR / "scram"))

# If DJANGO_SETTINGS_MODULE is unset, default to the local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# This application object is used by any ASGI server configured to use this file.
django_application = get_asgi_application()

# Events are published to a specific channel via api/views.py.
# Publishing to an event that's not routed will result in events that go nowhere.
application = ProtocolTypeRouter({
    "http": django_application,
    "websocket": URLRouter(scram_routing.websocket_urlpatterns),
    }
)
