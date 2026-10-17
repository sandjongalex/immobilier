"""Production future : exiger une configuration externe explicite."""
import os

from .base import *  # noqa: F403

DEBUG = False
if not ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS requis en production")  # noqa: F405
if not DATABASES["default"]["PASSWORD"]:  # noqa: F405
    raise ImproperlyConfigured("POSTGRES_PASSWORD requis en production")  # noqa: F405
if "DJANGO_MEDIA_ROOT" not in os.environ:
    raise ImproperlyConfigured("DJANGO_MEDIA_ROOT requis en production")  # noqa: F405

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_HSTS_SECONDS", "0"))
X_FRAME_OPTIONS = "DENY"
DATABASES["default"]["CONN_MAX_AGE"] = 60  # noqa: F405
