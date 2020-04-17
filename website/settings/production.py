# Production settings

from .base import *

SECRET_KEY = os.environ.get("SECRET_KEY", "")

DEBUG = False

ALLOWED_HOSTS = ["https://django-gallery-x17a.herokuapp.com/"]

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

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
