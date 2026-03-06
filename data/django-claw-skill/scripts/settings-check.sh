#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/load-config.sh"

TMPFILE=$(mktemp /tmp/django_query_XXXXXX.py)
trap 'rm -f "$TMPFILE"' EXIT

cat > "$TMPFILE" << PYEOF
import os, sys, re, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '${SETTINGS}')
sys.path.insert(0, '${PROJECT_PATH}')
django.setup()

from django.conf import settings

def mask_path(val):
    val = str(val)
    val = re.sub(r'/(Users|home)/[^/]+', r'/\1/***', val)
    return val

def mask_secret(val):
    s = str(val)
    if len(s) <= 8:
        return '***'
    return s[:4] + '***' + s[-4:]

print("=== Django Settings Check ===")
print(f"DEBUG:          {settings.DEBUG}")
print(f"ALLOWED_HOSTS:  {settings.ALLOWED_HOSTS}")
print(f"TIME_ZONE:      {settings.TIME_ZONE}")
print(f"LANGUAGE_CODE:  {settings.LANGUAGE_CODE}")
print(f"SECRET_KEY:     {mask_secret(settings.SECRET_KEY)}")
print(f"STATIC_URL:     {getattr(settings, 'STATIC_URL', 'NOT SET')}")
print(f"MEDIA_URL:      {getattr(settings, 'MEDIA_URL', 'NOT SET')}")
print(f"INSTALLED_APPS:")
for app in settings.INSTALLED_APPS:
    print(f"  - {app}")
print(f"DATABASES:")
for name, db in settings.DATABASES.items():
    print(f"  [{name}] ENGINE:   {db.get('ENGINE', '?')}")
    if 'NAME' in db:
        print(f"  [{name}] NAME:     {mask_path(db['NAME'])}")
    if db.get('USER'):
        print(f"  [{name}] USER:     ***")
    if db.get('PASSWORD'):
        print(f"  [{name}] PASSWORD: ***")
    if db.get('HOST'):
        print(f"  [{name}] HOST:     ***")
PYEOF

cd "$PROJECT_PATH"
"$PYTHON" "$TMPFILE"
