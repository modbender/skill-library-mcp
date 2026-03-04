#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="$HOME/.keepmyclaw"
CONFIG_FILE="$CONFIG_DIR/config"
PASSPHRASE_FILE="$CONFIG_DIR/passphrase"

echo "=== ClawKeeper Setup ==="
echo

mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

# API key
read -rp "API key (from keepmyclaw.com): " api_key
[[ -z "$api_key" ]] && echo "Error: API key cannot be empty" >&2 && exit 1

# Agent name
default_agent="$(hostname -s 2>/dev/null || echo "agent")"
read -rp "Agent name [${default_agent}]: " agent_name
agent_name="${agent_name:-$default_agent}"

# API URL
read -rp "API URL [https://api.keepmyclaw.com]: " api_url
api_url="${api_url:-https://api.keepmyclaw.com}"

# Write config
cat > "$CONFIG_FILE" <<EOF
CLAWKEEPER_API_KEY="${api_key}"
CLAWKEEPER_AGENT_NAME="${agent_name}"
CLAWKEEPER_API_URL="${api_url}"
EOF
chmod 600 "$CONFIG_FILE"
echo "✓ Config saved to $CONFIG_FILE"

# Passphrase
if [[ -f "$PASSPHRASE_FILE" ]]; then
    read -rp "Passphrase file exists. Overwrite? [y/N]: " overwrite
    if [[ "$overwrite" != [yY]* ]]; then
        echo "✓ Keeping existing passphrase"
    else
        read -rsp "Encryption passphrase: " passphrase; echo
        [[ -z "$passphrase" ]] && echo "Error: passphrase cannot be empty" >&2 && exit 1
        printf '%s' "$passphrase" > "$PASSPHRASE_FILE"
        chmod 600 "$PASSPHRASE_FILE"
        echo "✓ Passphrase saved"
    fi
else
    read -rsp "Encryption passphrase: " passphrase; echo
    [[ -z "$passphrase" ]] && echo "Error: passphrase cannot be empty" >&2 && exit 1
    printf '%s' "$passphrase" > "$PASSPHRASE_FILE"
    chmod 600 "$PASSPHRASE_FILE"
    echo "✓ Passphrase saved"
fi

# Test API connection
echo
echo "Testing API connection..."
HTTP_CODE="$(curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer ${api_key}" \
    "${api_url}/v1/account")"

if [[ "$HTTP_CODE" == "200" ]]; then
    echo "✓ Connected to Keep My Claw API"
else
    echo "✗ API returned HTTP ${HTTP_CODE}. Check your API key." >&2
    exit 1
fi

echo
echo "=== Setup complete ==="
echo "⚠ IMPORTANT: Back up your passphrase somewhere safe outside this machine!"
echo "  It is NOT included in backups and is required for restore."
