#!/usr/bin/env bash
set -euo pipefail

APP_DIR=${1:-}
shift || true

if [[ -z "${APP_DIR}" ]]; then
  echo "Usage: run_web_https.sh <app_dir> [--host 0.0.0.0] [--port 8443]" >&2
  exit 2
fi

HOST="0.0.0.0"
PORT="8443"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="$2"; shift 2;;
    --port) PORT="$2"; shift 2;;
    *) shift;;
  esac
done

cd "${APP_DIR}"
mkdir -p recordings

source venv/bin/activate

# Generate a self-signed cert if missing
if [[ ! -f cert.pem || ! -f key.pem ]]; then
  openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=maylo.local" >/dev/null 2>&1 || true
  chmod 600 key.pem cert.pem || true
fi

# Kill previous uvicorn
pkill -f "uvicorn webapp.server:app" 2>/dev/null || true

nohup uvicorn webapp.server:app --host "$HOST" --port "$PORT" --ssl-keyfile key.pem --ssl-certfile cert.pem > recordings/web.log 2>&1 &

echo "OK: web UI started"
echo "- URL: https://<mac-ip>:${PORT}"
echo "- Log: recordings/web.log"