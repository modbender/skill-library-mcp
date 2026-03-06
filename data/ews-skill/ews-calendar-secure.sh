#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="ews-calendar"

# Detect OS and get password from keyring
get_password() {
    local user="${EWS_USER:-}"
    
    if [[ -z "$user" ]]; then
        echo "[ERROR] EWS_USER not set" >&2
        return 1
    fi
    
    case "$(uname -s)" in
        Darwin)
            # macOS Keychain
            security find-generic-password \
                -a "$user" \
                -s "$SERVICE_NAME" \
                -w 2>/dev/null
            ;;
        Linux)
            # Linux libsecret
            secret-tool lookup \
                service "$SERVICE_NAME" \
                user "$user" 2>/dev/null
            ;;
        *)
            echo "[ERROR] Unsupported OS: $(uname -s)" >&2
            return 1
            ;;
    esac
}

# Check if keyring tools are available
check_dependencies() {
    case "$(uname -s)" in
        Darwin)
            if ! command -v security &>/dev/null; then
                echo "[ERROR] 'security' not found (macOS Keychain)" >&2
                return 1
            fi
            ;;
        Linux)
            if ! command -v secret-tool &>/dev/null; then
                echo "[ERROR] 'secret-tool' not found. Install: apt install libsecret-tools" >&2
                return 1
            fi
            ;;
    esac
}

main() {
    check_dependencies
    
    # Get password from keyring
    EWS_PASS=$(get_password)
    
    if [[ -z "$EWS_PASS" ]]; then
        echo "[ERROR] Password not found in keyring for user: ${EWS_USER:-<not set>}" >&2
        echo "[HINT] Run: ${SCRIPT_DIR}/ews-calendar-setup.sh to store credentials" >&2
        exit 1
    fi
    
    # Export and run main script
    export EWS_PASS
    exec "${SCRIPT_DIR}/ews-calendar.sh" "$@"
}

main "$@"
