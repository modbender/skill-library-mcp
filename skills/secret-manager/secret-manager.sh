#!/bin/bash
# secret-manager
# Securely manage API keys in GNOME Keyring and inject them into OpenClaw configuration.
#
# Usage:
#   secret-manager <KEY_NAME> [value]
#   secret-manager list
#   echo "val" | secret-manager <KEY_NAME>
#
# Configuration (Environment Variables):
#   OPENCLAW_CONTAINER  Name of the distrobox container (default: clawdbot)
#   OPENCLAW_HOME       Path to OpenClaw home (default: $HOME/.openclaw)
#   SECRETS_ENV_FILE    Path to an env file to source (optional)

set -euo pipefail

# --- Configuration ---
CONTAINER_NAME="${OPENCLAW_CONTAINER:-clawdbot}"
OPENCLAW_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}"
AUTH_PROFILES="$OPENCLAW_DIR/agents/main/agent/auth-profiles.json"
SECRETS_FILE="${SECRETS_ENV_FILE:-$HOME/.config/openclaw/secrets.env}"

# Key Definition: Env Var Name -> Keyring Service Name
declare -A SERVICES LABELS
SERVICES=(
    [OPENAI_API_KEY]="openai"
    [OPENAI_API_KEY_ALT]="openai-alt"
    [GOOGLE_PLACES_API_KEY]="google-places"
    [GEMINI_API_KEY]="gemini"
    [DISCORD_BOT_TOKEN]="discord-bot"
    [GATEWAY_AUTH_TOKEN]="gateway"
    [OLLAMA_API_KEY]="ollama"
    [GIPHY_API_KEY]="giphy"
    [LINKEDIN_LI_AT]="linkedin"
    [LINKEDIN_JSESSIONID]="linkedin"
    [GOOGLE_OAUTH_CLIENT_SECRET]="google-oauth"
)
LABELS=(
    [OPENAI_API_KEY]="OpenAI API Key"
    [OPENAI_API_KEY_ALT]="OpenAI API Key (Alt)"
    [GOOGLE_PLACES_API_KEY]="Google Places API Key"
    [GEMINI_API_KEY]="Gemini API Key"
    [DISCORD_BOT_TOKEN]="Discord Bot Token"
    [GATEWAY_AUTH_TOKEN]="Gateway Auth Token"
    [OLLAMA_API_KEY]="Ollama API Key"
    [GIPHY_API_KEY]="Giphy API Key"
    [LINKEDIN_LI_AT]="LinkedIn li_at Cookie"
    [LINKEDIN_JSESSIONID]="LinkedIn JSESSIONID"
    [GOOGLE_OAUTH_CLIENT_SECRET]="Google OAuth Client Secret"
)

# --- Dependency Check ---
if ! command -v secret-tool &> /dev/null; then
    echo "Error: 'secret-tool' not found. Please install libsecret-tools (Debian/Ubuntu) or libsecret (Fedora/Arch)."
    exit 1
fi

usage() {
    echo "Usage: secret-manager <KEY_NAME> [value]"
    echo "       secret-manager list"
    echo ""
    echo "Updates a secret in GNOME Keyring and restarts the gateway."
    echo ""
    echo "Supported Keys:"
    for key in $(echo "${!SERVICES[@]}" | tr ' ' '\n' | sort); do
        echo "  $key"
    done
    exit 1
}

list_keys() {
    echo "Configured secrets:"
    for key in $(echo "${!SERVICES[@]}" | tr ' ' '\n' | sort); do
        svc="${SERVICES[$key]}"
        val="$(secret-tool lookup service "$svc" key "$key" 2>/dev/null || true)"
        if [ -n "$val" ]; then
            echo "  $key = ${val:0:8}... (${#val} chars)"
        else
            echo "  $key = (not set)"
        fi
    done
}

[[ $# -lt 1 ]] && usage

if [[ "$1" == "list" ]]; then
    list_keys
    exit 0
fi

KEY_NAME="$1"

if [[ -z "${SERVICES[$KEY_NAME]+x}" ]]; then
    echo "Error: Unknown key '$KEY_NAME'"
    usage
fi

SERVICE="${SERVICES[$KEY_NAME]}"
LABEL="${LABELS[$KEY_NAME]}"

# Get the value
if [[ $# -ge 2 ]]; then
    VALUE="$2"
elif [[ ! -t 0 ]]; then
    VALUE="$(cat)"
else
    printf "Enter value for %s: " "$KEY_NAME"
    IFS= read -rs VALUE
    echo ""
fi

# Trim whitespace
VALUE="${VALUE%"${VALUE##*[![:space:]]}"}"

if [[ -z "$VALUE" ]]; then
    echo "Error: Empty value provided."
    exit 1
fi

echo "Storing $KEY_NAME..."
echo -n "$VALUE" | secret-tool store --label="$LABEL" service "$SERVICE" key "$KEY_NAME"

# Verify
VERIFY="$(secret-tool lookup service "$SERVICE" key "$KEY_NAME" 2>/dev/null)"
if [[ "$VERIFY" != "$VALUE" ]]; then
    echo "ERROR: Keyring verification failed."
    exit 1
fi

# --- Patch auth-profiles.json ---
# Maps Env Var -> Profile ID in auth-profiles.json
declare -A AUTH_PROFILE_MAP=(
    [GEMINI_API_KEY]="google:default"
    [OPENAI_API_KEY]="openai:default"
    [OPENAI_API_KEY_ALT]="openai:default"
)

if [[ -n "${AUTH_PROFILE_MAP[$KEY_NAME]+x}" ]]; then
    PROFILE_ID="${AUTH_PROFILE_MAP[$KEY_NAME]}"
    if [ -f "$AUTH_PROFILES" ]; then
        python3 -c "
import json, sys, os
path = sys.argv[1]
profile_id = sys.argv[2]
value = sys.argv[3]
try:
    with open(path) as f:
        data = json.load(f)
    if profile_id in data.get('profiles', {}):
        data['profiles'][profile_id]['key'] = value
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')
        print(f'Patched {profile_id} in {path}')
    else:
        print(f'Profile {profile_id} not found in config, skipping patch.')
except Exception as e:
    print(f'Error patching config: {e}')
" "$AUTH_PROFILES" "$PROFILE_ID" "$VALUE"
    else
        echo "Warning: Auth profiles file not found at $AUTH_PROFILES"
    fi
fi

# --- Propagate & Restart ---
if [ -f "$SECRETS_FILE" ]; then
    echo "Sourcing secrets from $SECRETS_FILE..."
    source "$SECRETS_FILE"
fi

echo "Importing environment to systemd user session..."
systemctl --user import-environment \
    OLLAMA_API_KEY DISCORD_BOT_TOKEN GATEWAY_AUTH_TOKEN \
    OPENAI_API_KEY OPENAI_API_KEY_ALT GOOGLE_PLACES_API_KEY \
    GEMINI_API_KEY GIPHY_API_KEY || true

echo "Restarting OpenClaw Gateway..."
systemctl --user stop openclaw-gateway.service 2>/dev/null || true

# Kill processes inside distrobox if it's running
if command -v distrobox &> /dev/null; then
    distrobox enter "$CONTAINER_NAME" -- bash -c '
        pkill -9 -f "openclaw-gateway" 2>/dev/null
        pkill -9 -f "openclaw$" 2>/dev/null
        sleep 1
        # Dynamic user ID path
        rm -f "/tmp/openclaw-$(id -u)/gateway.*.lock" 2>/dev/null
    ' 2>/dev/null || true
fi
sleep 2

systemctl --user start openclaw-gateway.service
sleep 5

if systemctl --user is-active --quiet openclaw-gateway.service; then
    echo "Success: Gateway restarted. $KEY_NAME is updated."
else
    echo "Warning: Gateway service did not start cleanly. Check logs."
fi
