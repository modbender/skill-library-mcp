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
print(f"{'Model':<40} {'Records':>10}")
print("-" * 52)
for model in apps.get_models():
    label = f"{model._meta.app_label}.{model.__name__}"
    try:
        count = model.objects.count()
    except Exception:
        count = "error"
    print(f"{label:<40} {str(count):>10}")
PYEOF

cd "$PROJECT_PATH"
"$PYTHON" "$TMPFILE"
