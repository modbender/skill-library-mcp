#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/load-config.sh"

LOG="$PROJECT_PATH/logs/django.log"

if [ -f "$LOG" ]; then
  echo "=== Last 50 lines of $LOG ==="
  tail -50 "$LOG"
else
  echo "No log file found at $LOG"
  echo ""
  echo "To enable logging, start Django with:"
  echo "  python manage.py runserver 2>&1 | tee $PROJECT_PATH/logs/django.log"
fi
