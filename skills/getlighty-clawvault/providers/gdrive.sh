#!/usr/bin/env bash
# ClawVault Provider — Google Drive
# Uses rclone for OAuth + sync
# Usage: gdrive.sh {setup|push|pull|test|info}

set -euo pipefail

VAULT_DIR="$HOME/.clawvault"
CONFIG="$VAULT_DIR/config.yaml"
PROVIDER_CONFIG="$VAULT_DIR/.provider-gdrive.json"
RCLONE_REMOTE="clawvault-gdrive"
REMOTE_DIR="ClawVault"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[clawvault:gdrive $(timestamp)] $*"; }

EXCLUDE="--exclude local/** --exclude keys/** --exclude .provider-*.json --exclude .cloud-provider.json --exclude .sync-* --exclude .pull-* --exclude .heartbeat.pid --exclude .git-local/** --exclude .git/**"

get_profile_name() {
  if [[ -n "${CLAWVAULT_PROFILE:-}" ]]; then echo "$CLAWVAULT_PROFILE"; return; fi
  local name
  name=$(grep 'profile_name:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  echo "${name:-$(hostname -s 2>/dev/null || echo default)}"
}

ensure_rclone() {
  if ! command -v rclone &>/dev/null; then
    log "rclone not found. Installing..."
    case "$(uname -s)" in
      Darwin) brew install rclone 2>/dev/null || curl https://rclone.org/install.sh | bash ;;
      Linux)  curl https://rclone.org/install.sh | sudo bash ;;
    esac
  fi
}

cmd_setup() {
  echo ""
  echo "📁 Google Drive Setup"
  echo "━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "This will open a browser window for Google OAuth."
  echo "Your vault will sync to: Google Drive / $REMOTE_DIR"
  echo ""

  ensure_rclone

  # Configure rclone remote
  log "Starting Google Drive OAuth..."
  rclone config create "$RCLONE_REMOTE" drive \
    scope "drive.file" 2>/dev/null || {
    log "Running interactive rclone config..."
    rclone config
  }

  # Create remote directory
  rclone mkdir "${RCLONE_REMOTE}:${REMOTE_DIR}" 2>/dev/null || true

  cat > "$PROVIDER_CONFIG" <<JSON
{
  "provider": "gdrive",
  "rclone_remote": "$RCLONE_REMOTE",
  "remote_dir": "$REMOTE_DIR",
  "configured": "$(timestamp)"
}
JSON

  log "✓ Google Drive configured"
  log "  Vault will sync to: Drive/$REMOTE_DIR"
}

cmd_push() {
  ensure_rclone
  local profile_name; profile_name=$(get_profile_name)
  local remote="${RCLONE_REMOTE}:${REMOTE_DIR}/profiles/$profile_name"
  log "Pushing to Google Drive (profile: $profile_name)..."
  rclone sync "$VAULT_DIR" "$remote" $EXCLUDE -v 2>&1 | grep -E "Transferred|Elapsed" || true
  log "Push to Google Drive complete (profile: $profile_name)"
}

cmd_pull() {
  ensure_rclone
  local pull_dir="$VAULT_DIR/.pull-gdrive"
  mkdir -p "$pull_dir"
  local profile_name; profile_name=$(get_profile_name)
  local remote="${RCLONE_REMOTE}:${REMOTE_DIR}/profiles/$profile_name"
  # Fallback to root if profiles/ doesn't exist
  if ! rclone lsd "${RCLONE_REMOTE}:${REMOTE_DIR}/profiles" &>/dev/null; then
    remote="${RCLONE_REMOTE}:${REMOTE_DIR}"
    log "No profiles found, falling back to root..."
  fi
  log "Pulling from Google Drive (profile: $profile_name)..."
  rclone sync "$remote" "$pull_dir" -v 2>&1 | grep -E "Transferred|Elapsed" || true

  # Merge (don't overwrite local/)
  for f in identity/USER.md knowledge/MEMORY.md requirements.yaml manifest.json identity/instances.yaml; do
    if [[ -f "$pull_dir/$f" ]]; then
      mkdir -p "$(dirname "$VAULT_DIR/$f")"
      cp "$pull_dir/$f" "$VAULT_DIR/$f"
    fi
  done
  [[ -d "$pull_dir/knowledge/projects" ]] && mkdir -p "$VAULT_DIR/knowledge/projects" && cp -r "$pull_dir/knowledge/projects/"* "$VAULT_DIR/knowledge/projects/" 2>/dev/null || true

  rm -rf "$pull_dir"
  log "Pull from Google Drive complete (profile: $profile_name)"
}

cmd_test() {
  ensure_rclone
  log "Testing Google Drive..."
  if rclone lsd "${RCLONE_REMOTE}:" &>/dev/null; then
    log "✓ Connected to Google Drive"
    local size
    size=$(rclone size "${RCLONE_REMOTE}:${REMOTE_DIR}" 2>/dev/null | grep "Total size" || echo "empty")
    log "  Vault size: $size"
  else
    log "✗ Cannot reach Google Drive. Re-run setup."
  fi
}

cmd_list_profiles() {
  ensure_rclone
  local current; current=$(get_profile_name)
  echo ""; echo "Remote Profiles"; echo "==============="
  if rclone lsd "${RCLONE_REMOTE}:${REMOTE_DIR}/profiles/" &>/dev/null; then
    rclone lsd "${RCLONE_REMOTE}:${REMOTE_DIR}/profiles/" 2>/dev/null | awk '{print $NF}' | while read -r p; do
      local marker=""; [[ "$p" == "$current" ]] && marker=" ← current"
      echo "  $p$marker"
    done
  else
    echo "  (no profiles yet)"
  fi
  echo ""
}

cmd_info() {
  if [[ -f "$PROVIDER_CONFIG" ]]; then
    echo "  Remote: Google Drive / $REMOTE_DIR"
    echo "  Via:    rclone ($RCLONE_REMOTE)"
    echo "  Profile: $(get_profile_name)"
  else
    echo "  Not configured"
  fi
}

case "${1:-info}" in
  setup) cmd_setup ;; push) cmd_push ;; pull) cmd_pull ;; test) cmd_test ;; info) cmd_info ;; list-profiles) cmd_list_profiles ;;
  *) echo "Usage: gdrive.sh {setup|push|pull|test|info|list-profiles}"; exit 1 ;;
esac
