#!/usr/bin/env bash
# ClawVault Provider — Dropbox (via rclone)
set -euo pipefail
VAULT_DIR="$HOME/.clawvault"; CONFIG="$VAULT_DIR/config.yaml"; PROVIDER_CONFIG="$VAULT_DIR/.provider-dropbox.json"
RCLONE_REMOTE="clawvault-dropbox"; REMOTE_DIR="ClawVault"
timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }; log() { echo "[clawvault:dropbox $(timestamp)] $*"; }

ensure_rclone() {
  if ! command -v rclone &>/dev/null; then
    log "rclone not found. Installing..."
    case "$(uname -s)" in
      Darwin) brew install rclone 2>/dev/null || curl https://rclone.org/install.sh | bash ;;
      Linux)  curl https://rclone.org/install.sh | sudo bash ;;
    esac
  fi
}

EXCLUDE="--exclude local/** --exclude keys/** --exclude .provider-*.json --exclude .cloud-provider.json --exclude .sync-* --exclude .pull-* --exclude .heartbeat.pid --exclude .git-local/** --exclude .git/**"

get_profile_name() {
  if [[ -n "${CLAWVAULT_PROFILE:-}" ]]; then echo "$CLAWVAULT_PROFILE"; return; fi
  local name
  name=$(grep 'profile_name:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  echo "${name:-$(hostname -s 2>/dev/null || echo default)}"
}

cmd_setup() {
  echo ""; echo "Dropbox Setup"; echo "==============="
  echo "This will open a browser window for Dropbox OAuth."
  echo "Your vault will sync to: Dropbox / Apps / $REMOTE_DIR"
  echo ""
  ensure_rclone
  log "Starting Dropbox OAuth..."
  rclone config create "$RCLONE_REMOTE" dropbox 2>/dev/null || { log "Running interactive rclone config..."; rclone config; }
  rclone mkdir "${RCLONE_REMOTE}:${REMOTE_DIR}" 2>/dev/null || true
  cat > "$PROVIDER_CONFIG" <<JSON
{"provider":"dropbox","rclone_remote":"$RCLONE_REMOTE","remote_dir":"$REMOTE_DIR","configured":"$(timestamp)"}
JSON
  log "Dropbox configured → Apps/$REMOTE_DIR"
}

cmd_push() {
  ensure_rclone
  local profile_name; profile_name=$(get_profile_name)
  local remote="${RCLONE_REMOTE}:${REMOTE_DIR}/profiles/$profile_name"
  log "Pushing to Dropbox (profile: $profile_name)..."
  rclone sync "$VAULT_DIR" "$remote" $EXCLUDE -v 2>&1 | grep -E "Transferred|Elapsed" || true
  log "Push to Dropbox complete (profile: $profile_name)"
}

cmd_pull() {
  ensure_rclone; local d="$VAULT_DIR/.pull-dropbox"; mkdir -p "$d"
  local profile_name; profile_name=$(get_profile_name)
  local remote="${RCLONE_REMOTE}:${REMOTE_DIR}/profiles/$profile_name"
  # Fallback to root if profiles/ doesn't exist
  if ! rclone lsd "${RCLONE_REMOTE}:${REMOTE_DIR}/profiles" &>/dev/null; then
    remote="${RCLONE_REMOTE}:${REMOTE_DIR}"
    log "No profiles found, falling back to root..."
  fi
  log "Pulling from Dropbox (profile: $profile_name)..."
  rclone sync "$remote" "$d" -v 2>&1 | grep -E "Transferred|Elapsed" || true
  for f in identity/USER.md knowledge/MEMORY.md requirements.yaml manifest.json identity/instances.yaml; do
    [[ -f "$d/$f" ]] && mkdir -p "$(dirname "$VAULT_DIR/$f")" && cp "$d/$f" "$VAULT_DIR/$f"
  done
  [[ -d "$d/knowledge/projects" ]] && mkdir -p "$VAULT_DIR/knowledge/projects" && cp -r "$d/knowledge/projects/"* "$VAULT_DIR/knowledge/projects/" 2>/dev/null || true
  rm -rf "$d"; log "Pull from Dropbox complete (profile: $profile_name)"
}

cmd_test() {
  ensure_rclone; log "Testing Dropbox..."
  rclone lsd "${RCLONE_REMOTE}:" &>/dev/null && log "Connected to Dropbox" || log "Cannot reach Dropbox. Re-run setup."
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
    echo "  Remote: Dropbox / Apps / $REMOTE_DIR (via rclone)"
    echo "  Profile: $(get_profile_name)"
  else echo "  Not configured"; fi
}

case "${1:-info}" in setup) cmd_setup;; push) cmd_push;; pull) cmd_pull;; test) cmd_test;; info) cmd_info;; list-profiles) cmd_list_profiles;; esac
