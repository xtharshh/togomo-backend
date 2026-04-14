import os
import sys
from pathlib import Path

# Ensure Django project package is importable when Vercel runs from /api.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "togomo_backend.settings")

from togomo_backend.wsgi import application as app
