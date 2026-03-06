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

from django.contrib.auth import get_user_model
User = get_user_model()

total = User.objects.count()
if total == 0:
    print("No users found in database")
else:
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<10} {'Active'}")
    print("-" * 75)
    for u in User.objects.all().order_by('id'):
        role = "superuser" if u.is_superuser else "staff" if u.is_staff else "user"
        print(f"{u.id:<5} {u.username:<20} {u.email:<30} {role:<10} {'✅' if u.is_active else '❌'}")
    print(f"\nTotal: {total} user(s)")
PYEOF

cd "$PROJECT_PATH"
"$PYTHON" "$TMPFILE"
