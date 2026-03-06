#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/load-config.sh"

TMPFILE=$(mktemp /tmp/django_query_XXXXXX.py)
trap 'rm -f "$TMPFILE"' EXIT

cat > "$TMPFILE" << PYEOF
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '${SETTINGS}')
sys.path.insert(0, '${PROJECT_PATH}')
django.setup()
from django.apps import apps
for app in apps.get_app_configs():
    print(f"{app.label} — {app.verbose_name} ({app.module.__name__})")
PYEOF

cd "$PROJECT_PATH"
"$PYTHON" "$TMPFILE"
