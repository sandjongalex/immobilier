"""Tests PostgreSQL : le runner crée une base de tests séparée."""
import os
from secrets import token_urlsafe

# Jeton volatile pour les tests, jamais un secret fixe ni une clé de production.
os.environ.setdefault("DJANGO_SECRET_KEY", token_urlsafe(48))

from .base import *  # noqa: E402,F403

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
DATABASES["default"]["TEST"] = {  # noqa: F405
    "NAME": f"test_{DATABASES['default']['NAME']}",  # noqa: F405
}
