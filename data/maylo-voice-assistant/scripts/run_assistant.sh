#!/usr/bin/env bash
set -euo pipefail

APP_DIR=${1:-}
if [[ -z "${APP_DIR}" ]]; then
  echo "Usage: run_assistant.sh <app_dir>" >&2
  exit 2
fi

cd "${APP_DIR}"
mkdir -p recordings

source venv/bin/activate
export PYTHONUNBUFFERED=1

# Optional tuning
export MAYLO_WAKE_THRESHOLD="${MAYLO_WAKE_THRESHOLD:-0.35}"
export MAYLO_WAKE_DEBUG="${MAYLO_WAKE_DEBUG:-0}"
export MAYLO_WAKE_FEEDBACK="${MAYLO_WAKE_FEEDBACK:-none}"
export MAYLO_POST_SAY_INHIBIT_SEC="${MAYLO_POST_SAY_INHIBIT_SEC:-4.0}"

# Kill previous
pkill -f "python .*bridge/milo_responder_openclaw.py" 2>/dev/null || true
pkill -f "python .*main.py --mode full" 2>/dev/null || true

nohup python -u bridge/milo_responder_openclaw.py > recordings/responder.log 2>&1 &
nohup python -u main.py --mode full > recordings/assistant.log 2>&1 &

echo "OK: assistant started"
echo "- recordings/assistant.log"
echo "- recordings/responder.log"