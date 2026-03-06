#!/bin/bash
#
# vault.sh - Moltbot skill wrapper for vaultctl
#
# This script is called by Moltbot to execute vault operations
# on the remote Mac via SSH tunnel.
#
# Usage:
#   ./vault.sh <command> [args...]
#
# Environment (required):
#   VAULT_SSH_USER  - Mac username
#
# Environment (optional):
#   VAULT_SSH_PORT  - SSH port for tunnel (default: 2222)
#   VAULT_SSH_HOST  - SSH host (default: localhost)
#
# Config fallback:
#   If VAULT_SSH_USER is not set, reads from
#   ~/.config/headless-vault-cli/mac-user (created by tunnel-setup.sh)
#

set -euo pipefail

# Auto-detect Mac username from config file if not set via env
VAULT_SSH_USER="${VAULT_SSH_USER:-}"
if [[ -z "$VAULT_SSH_USER" && -f "$HOME/.config/headless-vault-cli/mac-user" ]]; then
    VAULT_SSH_USER="$(cat "$HOME/.config/headless-vault-cli/mac-user")"
fi

VAULT_SSH_PORT="${VAULT_SSH_PORT:-2222}"
VAULT_SSH_HOST="${VAULT_SSH_HOST:-localhost}"
SSH_OPTS="-4 -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=yes"

if [[ -z "$VAULT_SSH_USER" ]]; then
    echo '{"error": "config_missing", "message": "Mac username not configured. Run tunnel-setup.sh or set VAULT_SSH_USER"}' >&2
    exit 1
fi

# Run vaultctl command on remote Mac
run_vaultctl() {
    ssh $SSH_OPTS -p "$VAULT_SSH_PORT" "${VAULT_SSH_USER}@${VAULT_SSH_HOST}" vaultctl "$@"
}

# Check if tunnel is up
check_tunnel() {
    if ! ssh $SSH_OPTS -p "$VAULT_SSH_PORT" "${VAULT_SSH_USER}@${VAULT_SSH_HOST}" vaultctl tree --depth 0 >/dev/null 2>&1; then
        echo '{"error": "tunnel_down", "message": "Cannot reach Mac. Is the tunnel running?"}' >&2
        exit 1
    fi
}

cmd="${1:-}"
shift || true

case "$cmd" in
    tree)
        args=()
        while [[ $# -gt 0 ]]; do
            case "$1" in
                depth=*) args+=(--depth "${1#depth=}") ;;
                all=true) args+=(--all) ;;
            esac
            shift
        done
        run_vaultctl tree "${args[@]}"
        ;;

    resolve)
        while [[ $# -gt 0 ]]; do
            case "$1" in
                path=*)
                    val="${1#path=}"
                    encoded=$(printf '%s' "$val" | base64)
                    run_vaultctl resolve --path "$encoded" --base64
                    exit
                    ;;
                title=*)
                    val="${1#title=}"
                    encoded=$(printf '%s' "$val" | base64)
                    run_vaultctl resolve --title "$encoded" --base64
                    exit
                    ;;
            esac
            shift
        done
        echo '{"error": "missing_param", "message": "Specify path= or title="}' >&2
        exit 1
        ;;

    info)
        path=""
        while [[ $# -gt 0 ]]; do
            case "$1" in
                path=*) path="${1#path=}" ;;
            esac
            shift
        done
        if [[ -z "$path" ]]; then
            echo '{"error": "missing_param", "message": "path= is required"}' >&2
            exit 1
        fi
        # Base64 encode path to handle spaces
        encoded_path=$(printf '%s' "$path" | base64)
        run_vaultctl info "$encoded_path" --base64
        ;;

    read)
        path=""
        while [[ $# -gt 0 ]]; do
            case "$1" in
                path=*) path="${1#path=}" ;;
            esac
            shift
        done
        if [[ -z "$path" ]]; then
            echo '{"error": "missing_param", "message": "path= is required"}' >&2
            exit 1
        fi
        # Base64 encode path to handle spaces
        encoded_path=$(printf '%s' "$path" | base64)
        run_vaultctl read "$encoded_path" --base64
        ;;

    create)
        path=""
        content=""
        while [[ $# -gt 0 ]]; do
            case "$1" in
                path=*) path="${1#path=}" ;;
                content=*) content="${1#content=}" ;;
            esac
            shift
        done
        if [[ -z "$path" || -z "$content" ]]; then
            echo '{"error": "missing_param", "message": "path= and content= are required"}' >&2
            exit 1
        fi
        # Base64 encode both path and content to handle spaces and special characters
        encoded_path=$(printf '%s' "$path" | base64)
        encoded_content=$(printf '%s' "$content" | base64)
        run_vaultctl create "$encoded_path" "$encoded_content" --base64
        ;;

    append)
        path=""
        content=""
        while [[ $# -gt 0 ]]; do
            case "$1" in
                path=*) path="${1#path=}" ;;
                content=*) content="${1#content=}" ;;
            esac
            shift
        done
        if [[ -z "$path" || -z "$content" ]]; then
            echo '{"error": "missing_param", "message": "path= and content= are required"}' >&2
            exit 1
        fi
        # Base64 encode both path and content to handle spaces and special characters
        encoded_path=$(printf '%s' "$path" | base64)
        encoded_content=$(printf '%s' "$content" | base64)
        run_vaultctl append "$encoded_path" "$encoded_content" --base64
        ;;

    set-root)
        echo '{"error": "not_allowed", "message": "set-root is a local-only admin command and cannot be run remotely"}' >&2
        exit 1
        ;;

    check)
        check_tunnel
        echo '{"status": "ok", "message": "Tunnel is up"}'
        ;;

    *)
        echo '{"error": "unknown_command", "message": "Unknown command: '"$cmd"'", "available": ["tree", "resolve", "info", "read", "create", "append", "check"]}' >&2
        exit 1
        ;;
esac
