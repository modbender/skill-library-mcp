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

from django.urls import get_resolver

def list_urls(patterns, prefix=''):
    for p in patterns:
        if hasattr(p, 'url_patterns'):
            list_urls(p.url_patterns, prefix + str(p.pattern))
        else:
            name = getattr(p, 'name', '') or ''
            view = getattr(p.callback, '__name__', str(p.callback))
            print(f"  {prefix}{p.pattern}  →  {view}  [{name}]")

print("Registered URL patterns:")
print("-" * 60)
list_urls(get_resolver().url_patterns)
PYEOF

cd "$PROJECT_PATH"
"$PYTHON" "$TMPFILE"
