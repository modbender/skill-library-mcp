#!/usr/bin/env bash
# ClawRoam Provider — WebDAV (Nextcloud, ownCloud, etc., via rclone)
set -euo pipefail
VAULT_DIR="$HOME/.clawroam"; CONFIG="$VAULT_DIR/config.yaml"; PROVIDER_CONFIG="$VAULT_DIR/.provider-webdav.json"
RCLONE_REMOTE="clawroam-webdav"; REMOTE_DIR="ClawRoam"
timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }; log() { echo "[clawroam:webdav $(timestamp)] $*"; }

ensure_rclone() {
  if ! command -v rclone &>/dev/null; then
    log "rclone not found. Installing..."
    case "$(uname -s)" in Darwin) brew install rclone 2>/dev/null || curl https://rclone.org/install.sh | bash ;; Linux) curl https://rclone.org/install.sh | sudo bash ;; esac
  fi
}

EXCLUDE="--exclude local/** --exclude keys/** --exclude .provider-*.json --exclude .cloud-provider.json --exclude .sync-* --exclude .pull-* --exclude .heartbeat.pid --exclude .git-local/** --exclude .git/**"

get_profile_name() {
  if [[ -n "${CLAWROAM_PROFILE:-}" ]]; then echo "$CLAWROAM_PROFILE"; return; fi
  local name
  name=$(grep 'profile_name:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  echo "${name:-$(hostname -s 2>/dev/null || echo default)}"
}

cmd_setup() {
  echo ""; echo "WebDAV Setup"; echo "============"
  echo "Works with Nextcloud, ownCloud, and any WebDAV server."
  echo ""
  read -rp "WebDAV URL (e.g. https://cloud.example.com/remote.php/dav/files/user): " url
  read -rp "Username: " user
  read -rsp "Password: " pass; echo ""
  read -rp "Remote directory [$REMOTE_DIR]: " rdir; rdir="${rdir:-$REMOTE_DIR}"

  if [[ -z "$url" || -z "$user" || -z "$pass" ]]; then
    log "URL, username, and password are required."; return 1
  fi

  ensure_rclone
  rclone config create "$RCLONE_REMOTE" webdav \
    url="$url" vendor="other" user="$user" pass="$(rclone obscure "$pass" 2>/dev/null || echo "$pass")" 2>/dev/null || { log "Running interactive rclone config..."; rclone config; }
  rclone mkdir "${RCLONE_REMOTE}:${rdir}" 2>/dev/null || true

  cat > "$PROVIDER_CONFIG" <<JSON
{"provider":"webdav","url":"$url","user":"$user","remote_dir":"$rdir","configured":"$(timestamp)"}
JSON
  log "WebDAV configured → $url/$rdir"
}

cmd_push() {
  ensure_rclone
  local rdir
  rdir=$(python3 -c "import json;print(json.load(open('$PROVIDER_CONFIG'))['remote_dir'])" 2>/dev/null || echo "$REMOTE_DIR")
  local profile_name; profile_name=$(get_profile_name)
  local remote="${RCLONE_REMOTE}:${rdir}/profiles/$profile_name"
  log "Pushing to WebDAV (profile: $profile_name)..."
  rclone sync "$VAULT_DIR" "$remote" $EXCLUDE -v 2>&1 | grep -E "Transferred|Elapsed" || true
  log "Push to WebDAV complete (profile: $profile_name)"
}

cmd_pull() {
  ensure_rclone; local d="$VAULT_DIR/.pull-webdav"; mkdir -p "$d"
  local rdir
  rdir=$(python3 -c "import json;print(json.load(open('$PROVIDER_CONFIG'))['remote_dir'])" 2>/dev/null || echo "$REMOTE_DIR")
  local profile_name; profile_name=$(get_profile_name)
  local remote="${RCLONE_REMOTE}:${rdir}/profiles/$profile_name"
  # Fallback to root if profiles/ doesn't exist
  if ! rclone lsd "${RCLONE_REMOTE}:${rdir}/profiles" &>/dev/null; then
    remote="${RCLONE_REMOTE}:${rdir}"
    log "No profiles found, falling back to root..."
  fi
  log "Pulling from WebDAV (profile: $profile_name)..."
  rclone sync "$remote" "$d" -v 2>&1 | grep -E "Transferred|Elapsed" || true
  for f in identity/USER.md knowledge/MEMORY.md requirements.yaml manifest.json identity/instances.yaml; do
    [[ -f "$d/$f" ]] && mkdir -p "$(dirname "$VAULT_DIR/$f")" && cp "$d/$f" "$VAULT_DIR/$f"
  done
  [[ -d "$d/knowledge/projects" ]] && mkdir -p "$VAULT_DIR/knowledge/projects" && cp -r "$d/knowledge/projects/"* "$VAULT_DIR/knowledge/projects/" 2>/dev/null || true
  rm -rf "$d"; log "Pull from WebDAV complete (profile: $profile_name)"
}

cmd_test() {
  ensure_rclone; log "Testing WebDAV..."
  rclone lsd "${RCLONE_REMOTE}:" &>/dev/null && log "Connected to WebDAV" || log "Cannot reach WebDAV. Re-run setup."
}

cmd_list_profiles() {
  ensure_rclone
  local rdir
  rdir=$(python3 -c "import json;print(json.load(open('$PROVIDER_CONFIG'))['remote_dir'])" 2>/dev/null || echo "$REMOTE_DIR")
  local current; current=$(get_profile_name)
  echo ""; echo "Remote Profiles"; echo "==============="
  if rclone lsd "${RCLONE_REMOTE}:${rdir}/profiles/" &>/dev/null; then
    rclone lsd "${RCLONE_REMOTE}:${rdir}/profiles/" 2>/dev/null | awk '{print $NF}' | while read -r p; do
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
    local url rdir
    url=$(python3 -c "import json;print(json.load(open('$PROVIDER_CONFIG'))['url'])" 2>/dev/null || echo "?")
    rdir=$(python3 -c "import json;print(json.load(open('$PROVIDER_CONFIG'))['remote_dir'])" 2>/dev/null || echo "?")
    echo "  Remote: $url/$rdir (via rclone)"
    echo "  Profile: $(get_profile_name)"
  else echo "  Not configured"; fi
}

case "${1:-info}" in setup) cmd_setup;; push) cmd_push;; pull) cmd_pull;; test) cmd_test;; info) cmd_info;; list-profiles) cmd_list_profiles;; esac
