"""
WSGI config for farmIT project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Ensure the project root is on sys.path for serverless environments (case-sensitive FS)
BASE_DIR = Path(__file__).resolve().parent.parent  # /.../farmIT/farmIT
ROOT_DIR = BASE_DIR.parent                         # /.../farmIT
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmIT.settings')

application = get_wsgi_application()

# Vercel requires 'app' instead of 'application'
app = application