#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/load-config.sh"

if [ -z "${1:-}" ]; then
  echo "ERROR: No Python code provided."
  echo "Usage: run-query.sh \"<python code>\""
  echo "Example: run-query.sh \"from core.models import Organisation; print(Organisation.objects.count())\""
  exit 1
fi

# Block access to sensitive settings values
if printf '%s' "$1" | grep -qiE '(SECRET_KEY|AWS_SECRET|API_KEY|PRIVATE_KEY|PASSWORD|\.conf\s+import\s+settings)'; then
  echo "ERROR: Accessing sensitive settings is not permitted via django-claw shell."
  exit 1
fi

if [ "$READ_ONLY" = "true" ]; then
  echo "⛔ Read-only mode: 'shell' is disabled. Run 'django-claw readonly off' to enable."
  exit 1
fi

TMPFILE=$(mktemp /tmp/django_query_XXXXXX.py)
trap 'rm -f "$TMPFILE"' EXIT

# Write Django boilerplate (heredoc — only our trusted vars expand here)
cat > "$TMPFILE" << PYEOF
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '${SETTINGS}')
sys.path.insert(0, '${PROJECT_PATH}')
django.setup()

PYEOF

# Append user code safely — printf avoids heredoc variable/command expansion
printf '%s\n' "$1" >> "$TMPFILE"

cd "$PROJECT_PATH"
"$PYTHON" "$TMPFILE"
