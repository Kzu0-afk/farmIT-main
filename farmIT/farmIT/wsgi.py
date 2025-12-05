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
# Add paths so Django can find the settings module on Vercel (case-sensitive FS)
BASE_DIR = Path(__file__).resolve().parent.parent  # /.../farmIT/farmIT -> /.../farmIT
PROJECT_ROOT = BASE_DIR.parent                     # /.../ (serverless task root)
REPO_ROOT = PROJECT_ROOT.parent                    # one level above task root
for path in (str(BASE_DIR), str(PROJECT_ROOT), str(REPO_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmIT.settings')

application = get_wsgi_application()

# Vercel requires 'app' instead of 'application'
app = application