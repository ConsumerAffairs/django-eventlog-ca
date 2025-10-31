"""
Django settings for eventlog tests.
"""

SECRET_KEY = "test-secret-key-for-eventlog"

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django_extensions",
    "eventlog",
]

USE_TZ = True

# Disable Pusher for tests
PUSHER_CONFIG = None
