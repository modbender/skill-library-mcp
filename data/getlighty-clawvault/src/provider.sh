#!/usr/bin/env bash
# ClawVault — Provider Manager
# Routes to provider-specific scripts and manages provider config
# Usage: provider.sh {setup|list|test|info} [provider_name]

set -euo pipefail

VAULT_DIR="$HOME/.clawvault"
CONFIG="$VAULT_DIR/config.yaml"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROVIDERS_DIR="$SCRIPT_DIR/../providers"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[clawvault:provider $(timestamp)] $*"; }

cmd_list() {
  echo ""
  echo "Available Storage Providers"
  echo "==========================="
  echo ""
  echo "  cloud     ClawVault Cloud (managed, 50 MB free)"
  echo "  gdrive    Google Drive (via rclone)"
  echo "  dropbox   Dropbox (via rclone)"
  echo "  ftp       FTP/SFTP server (via rsync+ssh)"
  echo "  git       Any Git remote (GitHub, GitLab, etc.)"
  echo "  s3        S3-compatible bucket (via rclone)"
  echo "  webdav    WebDAV (Nextcloud, etc., via rclone)"
  echo "  local     Local directory (USB/NAS mount)"
  echo ""
  echo "Setup: clawvault.sh provider setup <name>"
  echo ""
}

cmd_setup() {
  local provider="${1:-}"

  if [[ -z "$provider" ]]; then
    echo "Usage: clawvault.sh provider setup <name>"
    cmd_list
    return 1
  fi

  local script="$PROVIDERS_DIR/${provider}.sh"
  if [[ ! -f "$script" ]]; then
    log "Unknown provider: $provider"
    cmd_list
    return 1
  fi

  if [[ ! -f "$CONFIG" ]]; then
    log "Vault not initialized. Run 'clawvault.sh init' first."
    return 1
  fi

  # Run provider setup
  bash "$script" setup

  # Update config.yaml with selected provider
  if [[ "$(uname -s)" == "Darwin" ]]; then
    sed -i '' "s/^provider: .*/provider: \"$provider\"/" "$CONFIG"
  else
    sed -i "s/^provider: .*/provider: \"$provider\"/" "$CONFIG"
  fi

  log "Provider set to: $provider"
}

cmd_test() {
  local provider="${1:-}"

  if [[ -z "$provider" ]]; then
    provider=$(grep '^provider:' "$CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"')
  fi

  if [[ -z "$provider" ]]; then
    log "No provider configured."
    return 1
  fi

  local script="$PROVIDERS_DIR/${provider}.sh"
  if [[ -f "$script" ]]; then
    bash "$script" test
  else
    log "Provider script not found: $provider"
    return 1
  fi
}

cmd_info() {
  local provider="${1:-}"

  if [[ -z "$provider" ]]; then
    provider=$(grep '^provider:' "$CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"')
  fi

  if [[ -z "$provider" ]]; then
    echo "No provider configured."
    return 0
  fi

  local script="$PROVIDERS_DIR/${provider}.sh"
  if [[ -f "$script" ]]; then
    bash "$script" info
  else
    echo "Provider: $provider (script not found)"
  fi
}

case "${1:-list}" in
  setup) cmd_setup "${2:-}" ;;
  list)  cmd_list ;;
  test)  cmd_test "${2:-}" ;;
  info)  cmd_info "${2:-}" ;;
  *)     echo "Usage: provider.sh {setup|list|test|info} [provider_name]"; exit 1 ;;
esac
