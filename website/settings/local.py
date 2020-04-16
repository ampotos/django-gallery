# Development settings

from .base import *

SECRET_KEY = "1_p8o)y&h-$@@=rwriz9t227**z1p2e+mp6o%1e(3pe8jsb&&v"

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "StlViewer",
        "USER": "test",
        "PASSWORD": "test",
        "HOST": "localhost",
        "PORT": "",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "admin@localhost"
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
EMAIL_PORT = 1025

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
# STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
