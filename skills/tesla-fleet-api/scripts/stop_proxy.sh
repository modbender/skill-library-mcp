#!/usr/bin/env bash
set -e

# Stop tesla-http-proxy.

# --- Resolve workspace ---
if [ -n "$OPENCLAW_WORKSPACE" ]; then
    WORKSPACE="$OPENCLAW_WORKSPACE"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    WORKSPACE="$(cd "$SCRIPT_DIR" && while [ "$PWD" != "/" ]; do
        [ -d skills ] && echo "$PWD" && break; cd ..; done)"
    [ -z "$WORKSPACE" ] && WORKSPACE="$HOME/clawd"
fi

PID_FILE="${WORKSPACE}/tesla-fleet-api/proxy/proxy.pid"

if [ ! -f "${PID_FILE}" ]; then
    echo "Proxy is not running (no PID file)"
    exit 0
fi

PROXY_PID=$(cat "${PID_FILE}")

if ! ps -p "${PROXY_PID}" > /dev/null 2>&1; then
    echo "Proxy is not running (stale PID file)"
    rm -f "${PID_FILE}"
    exit 0
fi

echo "Stopping tesla-http-proxy (PID: ${PROXY_PID})..."
kill "${PROXY_PID}"

for i in $(seq 1 10); do
    if ! ps -p "${PROXY_PID}" > /dev/null 2>&1; then
        rm -f "${PID_FILE}"
        echo "✓ Proxy stopped"
        exit 0
    fi
    sleep 0.5
done

kill -9 "${PROXY_PID}" 2>/dev/null
rm -f "${PID_FILE}"
echo "✓ Proxy stopped (forced)"
