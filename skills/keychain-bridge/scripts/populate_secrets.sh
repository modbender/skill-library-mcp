#!/bin/bash
# Populate secrets files from keychain before service start.
# Group B: secrets that bash scripts or config files need as files on disk.
#
# Usage:
#   1. Edit GROUP_B_SERVICES below to list your secret names
#   2. Run this script from your LaunchAgent or startup sequence
#   3. Bash scripts can then: MY_SECRET=$(cat $SECRETS_DIR/my-service)
#
# IMPORTANT: This script calls get_secret.py directly. It works because
# it's typically run early in boot from a Python-native context or terminal.
# If called from a bash LaunchAgent, get_secret.py may hang — in that case,
# make this script itself a Python LaunchAgent (see migrate_secrets.py).

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SECRETS_DIR="${SECRETS_DIR:-$HOME/.openclaw/secrets}"
ACCOUNT="${ACCOUNT:-moltbot}"

# --- Edit this list for your environment ---
GROUP_B_SERVICES=(
    # Add your Group B service names here, one per line:
    # "my-api-key"
    # "my-webhook-token"
)

mkdir -p "$SECRETS_DIR"

populated=0
failed=0

for svc in "${GROUP_B_SERVICES[@]}"; do
    value=$(python3 "$SCRIPT_DIR/get_secret.py" "$svc" --account "$ACCOUNT" 2>/dev/null)
    if [ -n "$value" ]; then
        echo -n "$value" > "$SECRETS_DIR/$svc"
        chmod 600 "$SECRETS_DIR/$svc"
        populated=$((populated + 1))
    else
        echo "WARNING: $svc not found in keychain" >&2
        failed=$((failed + 1))
    fi
done

echo "Populated $populated secrets ($failed failed) into $SECRETS_DIR"
