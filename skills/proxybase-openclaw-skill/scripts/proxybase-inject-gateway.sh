#!/usr/bin/env bash
# proxybase-inject-gateway.sh — Inject a proxy into the OpenClaw systemd service
# Usage: bash proxybase-inject-gateway.sh <order_id>
#
# This script injects the SOCKS5 proxy URL from a specific order
# into ~/.config/systemd/user/openclaw-gateway.service and restarts the gateway.

set -euo pipefail

# Source shared library
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

ORDER_ID="${1:-}"

if [[ -z "$ORDER_ID" ]]; then
    echo "ERROR: order_id is required"
    echo "Usage: bash proxybase-inject-gateway.sh <order_id>"
    exit 1
fi

init_orders_file

# Extract the proxy URL for the given order
acquire_lock
PROXY_URL=$(jq -r --arg oid "$ORDER_ID" '.orders[] | select(.order_id == $oid) | .proxy // empty' "$ORDERS_FILE" 2>/dev/null)
release_lock

if [[ -z "$PROXY_URL" ]]; then
    echo "ERROR: Could not find an active proxy URL for order $ORDER_ID"
    exit 1
fi

SERVICE_FILE="$HOME/.config/systemd/user/openclaw-gateway.service"

if [[ ! -f "$SERVICE_FILE" ]]; then
    echo "ERROR: Systemd service file not found at $SERVICE_FILE"
    echo "Cannot inject proxy configuration."
    exit 1
fi

# Verify the service file contains a [Service] section
if ! grep -q '^\[Service\]' "$SERVICE_FILE"; then
    echo "ERROR: No [Service] section found in $SERVICE_FILE"
    echo "Cannot inject proxy environment variables."
    exit 1
fi

echo "ProxyBase: Injecting proxy into $SERVICE_FILE..."

# Backup the service file
cp "$SERVICE_FILE" "${SERVICE_FILE}.bak"

# 1. Remove existing Proxy Environment lines to avoid duplicates
# Use sed with separate -i '' for macOS/BSD compatibility (this script
# targets Linux/systemd, but be safe in case of cross-platform testing).
if sed --version 2>/dev/null | grep -q 'GNU'; then
    sed -i '/^Environment=HTTP_PROXY=/d;/^Environment=HTTPS_PROXY=/d;/^Environment=NODE_USE_ENV_PROXY=/d' "$SERVICE_FILE"
else
    sed -i '' '/^Environment=HTTP_PROXY=/d;/^Environment=HTTPS_PROXY=/d;/^Environment=NODE_USE_ENV_PROXY=/d' "$SERVICE_FILE"
fi

# 2. Inject the new lines right after the [Service] declaration
# Use awk to cleanly append immediately after the [Service] line
awk -v proxy="$PROXY_URL" '
/^\[Service\]/ {
    print $0
    print "Environment=HTTP_PROXY=" proxy
    print "Environment=HTTPS_PROXY=" proxy
    print "Environment=NODE_USE_ENV_PROXY=1"
    next
}
{ print $0 }
' "$SERVICE_FILE" > "${SERVICE_FILE}.new"

# Validate the rewritten file before replacing
if [[ ! -s "${SERVICE_FILE}.new" ]]; then
    echo "ERROR: awk produced an empty output — aborting. Original file restored from .bak" >&2
    cp "${SERVICE_FILE}.bak" "$SERVICE_FILE"
    rm -f "${SERVICE_FILE}.new"
    exit 1
fi

if ! grep -q 'Environment=HTTP_PROXY=' "${SERVICE_FILE}.new"; then
    echo "ERROR: Proxy environment lines not found in rewritten file — aborting." >&2
    cp "${SERVICE_FILE}.bak" "$SERVICE_FILE"
    rm -f "${SERVICE_FILE}.new"
    exit 1
fi

mv "${SERVICE_FILE}.new" "$SERVICE_FILE"

echo "ProxyBase: Configuration updated successfully."
echo "  HTTP_PROXY=$PROXY_URL"
echo "  HTTPS_PROXY=$PROXY_URL"
echo "  NODE_USE_ENV_PROXY=1"
echo ""

# Restart the process
echo "ProxyBase: Reloading systemd daemon..."
if command -v systemctl >/dev/null 2>&1; then
    systemctl --user daemon-reload || {
        echo "WARN: systemctl --user daemon-reload failed."
    }
else
    echo "WARN: systemctl not found."
fi

echo "ProxyBase: Restarting OpenClaw Gateway..."
if command -v openclaw >/dev/null 2>&1; then
    openclaw gateway restart || {
        echo "ERROR: Failed to run 'openclaw gateway restart'."
        exit 1
    }
else
    echo "ERROR: 'openclaw' command not found. Cannot restart the gateway."
    exit 1
fi

echo "✅ Success! OpenClaw Gateway is now routing traffic through proxy $ORDER_ID."
exit 0
