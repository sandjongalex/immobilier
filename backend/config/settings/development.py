"""Mode local : serveur non destiné à Internet."""
from .base import *  # noqa: F403

DEBUG = True
if not ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
