#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/load-config.sh"

if [ "$READ_ONLY" = "true" ] && { [ "${1:-}" = "migrate" ] || [ "${1:-}" = "makemigrations" ]; }; then
  echo "⛔ Read-only mode: '${1}' is disabled. Run 'django-claw readonly off' to enable."
  exit 1
fi

if [ -z "${1:-}" ]; then
  echo "ERROR: No management command provided."
  echo "Usage: run.sh <command> [args]"
  echo "Example: run.sh showmigrations"
  exit 1
fi

cd "$PROJECT_PATH"
export DJANGO_SETTINGS_MODULE="$SETTINGS"
exec "$PYTHON" manage.py "$@"
