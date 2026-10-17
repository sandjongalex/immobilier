"""Entrée ASGI pour exécution compatible ASGI (sans serveur ajouté en V1)."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
application = get_asgi_application()
