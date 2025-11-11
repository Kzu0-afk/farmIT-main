release: python farmIT/manage.py migrate --noinput
web: gunicorn farmIT.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-3} --threads ${WEB_THREADS:-2}

