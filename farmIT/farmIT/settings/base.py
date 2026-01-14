from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
_TEMPLATE_DIRS = [BASE_DIR / 'templates', BASE_DIR.parent / 'templates']
TEMPLATE_DIRS = [p for p in _TEMPLATE_DIRS if p.exists()]

# Load .env if available (safe in dev; ignored if package not installed)
try:
    from dotenv import load_dotenv, find_dotenv  # type: ignore
    load_dotenv(find_dotenv(), override=False)
    load_dotenv(dotenv_path=(BASE_DIR.parent / '.env'), override=False)
    load_dotenv(dotenv_path=(BASE_DIR / '.env'), override=False)
except Exception:
    pass

# SECURITY: default to False in base; dev/prod override explicitly
DEBUG = False

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'insecure-dev-key-change-me')

ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = [u.strip() for u in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if u.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Local apps
    'users',
    'products',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Simple per-IP rate limiting (anti-ddos)
    'farmIT.middleware.RateLimitMiddleware',
]

ROOT_URLCONF = 'farmIT.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATE_DIRS,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'farmIT.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

_database_url = os.getenv('DATABASE_URL')
if _database_url:
    try:
        import dj_database_url  # type: ignore
        conn_max_age = int(os.getenv('DB_CONN_MAX_AGE', '600'))
        ssl_require = os.getenv('DB_SSL_REQUIRE', 'true').lower() in ('1', 'true', 'yes')
        DATABASES['default'] = dj_database_url.parse(
            _database_url,
            conn_max_age=conn_max_age,
            ssl_require=ssl_require,
        )
    except Exception:
        pass

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# Leave storage class to prod; dev will use default

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'farmit-cache',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.FarmerUser'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# Rate limiting configuration
# In proxy deployments (Vercel), X-Forwarded-For is the reliable source of client IP.
RATE_LIMIT_TRUST_X_FORWARDED_FOR = os.getenv("RATE_LIMIT_TRUST_X_FORWARDED_FOR", "true").lower() in ("1", "true", "yes")


