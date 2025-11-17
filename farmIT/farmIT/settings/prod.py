from .base import *  # noqa: F401,F403
import os

DEBUG = False

# Enforce that a proper secret key is set in production
if SECRET_KEY == 'insecure-dev-key-change-me':
    # Keep running but warn via logging; operators should set DJANGO_SECRET_KEY
    import warnings
    warnings.warn("DJANGO_SECRET_KEY is using an insecure default in production.", RuntimeWarning)

# Security headers and HTTPS
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files: compression/manifest
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Minimal logging (avoid verbose request/SQL logs)
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
        'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
    },
    'loggers': {
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}


