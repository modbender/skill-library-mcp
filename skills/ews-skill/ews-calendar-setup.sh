#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="ews-calendar"

show_help() {
    cat << EOF
EWS Calendar Credential Setup

Stores EWS credentials securely in OS keyring.

Usage: $(basename "$0") [OPTIONS]

Options:
  -u, --user USER       Domain\username (required)
  -p, --password PASS   Password (will prompt if not provided)
      --delete          Remove stored credentials for user
  -h, --help            Show this message

Examples:
  $(basename "$0") --user "DOMAIN\\jsmith"
  $(basename "$0") -u "DOMAIN\\jsmith" -p "mypassword"
  $(basename "$0") --user "DOMAIN\\jsmith" --delete

After setup, test with:
  ./ews-calendar-secure.sh --date today

Configure EWS_URL and EWS_USER in ~/.openclaw/openclaw.json:
{
  skills: {
    entries: {
      "ews-calendar": {
        enabled: true,
        env: {
          EWS_URL: "https://outlook.company.com/EWS/Exchange.asmx",
          EWS_USER: "DOMAIN\\jsmith"
        }
      }
    }
  }
}
EOF
    exit 0
}

store_credential() {
    local user="$1"
    local password="$2"
    
    case "$(uname -s)" in
        Darwin)
            # Delete existing entry if present, then add
            security delete-generic-password -a "$user" -s "$SERVICE_NAME" 2>/dev/null || true
            security add-generic-password \
                -a "$user" \
                -s "$SERVICE_NAME" \
                -w "$password"
            echo "✓ Credential stored in macOS Keychain"
            ;;
        Linux)
            echo -n "$password" | secret-tool store \
                --label="EWS Calendar" \
                service "$SERVICE_NAME" \
                user "$user"
            echo "✓ Credential stored in libsecret keyring"
            ;;
        *)
            echo "[ERROR] Unsupported OS: $(uname -s)" >&2
            exit 1
            ;;
    esac
}

delete_credential() {
    local user="$1"
    
    case "$(uname -s)" in
        Darwin)
            if security delete-generic-password -a "$user" -s "$SERVICE_NAME" 2>/dev/null; then
                echo "✓ Credential removed from macOS Keychain"
            else
                echo "ℹ No credential found for user: $user"
            fi
            ;;
        Linux)
            if secret-tool clear service "$SERVICE_NAME" user "$user" 2>/dev/null; then
                echo "✓ Credential removed from libsecret keyring"
            else
                echo "ℹ No credential found for user: $user"
            fi
            ;;
    esac
}

# Parse arguments
USER=""
PASSWORD=""
DELETE_MODE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -u|--user)
            USER="$2"
            shift 2
            ;;
        -p|--password)
            PASSWORD="$2"
            shift 2
            ;;
        --delete)
            DELETE_MODE=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "[ERROR] Unknown option: $1" >&2
            show_help
            ;;
    esac
done

if [[ -z "$USER" ]]; then
    echo "[ERROR] User is required. Use --user 'DOMAIN\\username'" >&2
    exit 1
fi

# Delete mode
if [[ "$DELETE_MODE" == true ]]; then
    delete_credential "$USER"
    exit 0
fi

# Prompt for password if not provided
if [[ -z "$PASSWORD" ]]; then
    read -s -p "Enter password for $USER: " PASSWORD
    echo
fi

if [[ -z "$PASSWORD" ]]; then
    echo "[ERROR] Password cannot be empty" >&2
    exit 1
fi

# Store credential
store_credential "$USER" "$PASSWORD"

echo ""
echo "Credential stored securely."
echo "Next: Configure EWS_URL and EWS_USER in ~/.openclaw/openclaw.json"
