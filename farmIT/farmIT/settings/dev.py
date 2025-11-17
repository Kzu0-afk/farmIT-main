from .base import *  # noqa: F401,F403

# Dev-friendly defaults
DEBUG = True

# Keep insecure key for local only; set DJANGO_SECRET_KEY in prod
# SECRET_KEY inherited from base (env-backed with insecure default)

# Static files served by Django in dev; WhiteNoise storage not required here

# Logging: be verbose in dev if needed
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}


