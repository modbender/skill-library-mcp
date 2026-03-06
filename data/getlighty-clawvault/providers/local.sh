#!/usr/bin/env bash
# ClawVault Provider — Local directory (USB drive, NAS mount, shared folder)
set -euo pipefail
VAULT_DIR="$HOME/.clawvault"; CONFIG="$VAULT_DIR/config.yaml"; PROVIDER_CONFIG="$VAULT_DIR/.provider-local.json"
timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }; log() { echo "[clawvault:local $(timestamp)] $*"; }

EXCLUDE="--exclude local/ --exclude keys/ --exclude .provider-*.json --exclude .cloud-provider.json --exclude .sync-* --exclude .pull-* --exclude .heartbeat.pid --exclude .git-local/ --exclude .git/"

get_profile_name() {
  if [[ -n "${CLAWVAULT_PROFILE:-}" ]]; then echo "$CLAWVAULT_PROFILE"; return; fi
  local name
  name=$(grep 'profile_name:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  echo "${name:-$(hostname -s 2>/dev/null || echo default)}"
}

cmd_setup() {
  echo ""; echo "Local Storage Setup"; echo "==================="
  echo "Use a USB drive, NAS mount, or any local/network directory."
  echo ""
  read -rp "Directory path (e.g. /Volumes/USB/clawvault or /mnt/nas/clawvault): " target_dir
  if [[ -z "$target_dir" ]]; then log "Path required."; return 1; fi

  if [[ ! -d "$target_dir" ]]; then
    read -rp "Directory doesn't exist. Create it? [Y/n]: " yn
    if [[ "$yn" =~ ^[Nn] ]]; then return 1; fi
    mkdir -p "$target_dir" || { log "Cannot create directory."; return 1; }
  fi

  cat > "$PROVIDER_CONFIG" <<JSON
{"provider":"local","path":"$target_dir","configured":"$(timestamp)"}
JSON
  log "Local storage configured → $target_dir"
}

_get_path() {
  python3 -c "import json;print(json.load(open('$PROVIDER_CONFIG'))['path'])" 2>/dev/null
}

cmd_push() {
  if [[ ! -f "$PROVIDER_CONFIG" ]]; then log "Not configured."; return 1; fi
  local target; target=$(_get_path)
  if [[ ! -d "$target" ]]; then log "Target not found: $target"; return 1; fi
  local profile_name; profile_name=$(get_profile_name)
  local target_profile="$target/profiles/$profile_name"
  mkdir -p "$target_profile"
  log "Pushing to $target_profile..."
  rsync -a --delete $EXCLUDE "$VAULT_DIR/" "$target_profile/" 2>&1 | tail -3
  log "Push complete (profile: $profile_name)"
}

cmd_pull() {
  if [[ ! -f "$PROVIDER_CONFIG" ]]; then log "Not configured."; return 1; fi
  local target; target=$(_get_path)
  if [[ ! -d "$target" ]]; then log "Target not found: $target"; return 1; fi
  local profile_name; profile_name=$(get_profile_name)
  local source_dir="$target/profiles/$profile_name"
  [[ ! -d "$source_dir" ]] && source_dir="$target"
  log "Pulling from $source_dir..."
  for f in identity/USER.md knowledge/MEMORY.md requirements.yaml manifest.json identity/instances.yaml; do
    [[ -f "$source_dir/$f" ]] && mkdir -p "$(dirname "$VAULT_DIR/$f")" && cp "$source_dir/$f" "$VAULT_DIR/$f"
  done
  [[ -d "$source_dir/knowledge/projects" ]] && mkdir -p "$VAULT_DIR/knowledge/projects" && cp -r "$source_dir/knowledge/projects/"* "$VAULT_DIR/knowledge/projects/" 2>/dev/null || true
  log "Pull complete (profile: $profile_name)"
}

cmd_list_profiles() {
  if [[ ! -f "$PROVIDER_CONFIG" ]]; then log "Not configured."; return 1; fi
  local target; target=$(_get_path)
  local current; current=$(get_profile_name)
  echo ""; echo "Remote Profiles"; echo "==============="
  if [[ -d "$target/profiles" ]]; then
    ls -1 "$target/profiles/" 2>/dev/null | while read -r p; do
      local marker=""; [[ "$p" == "$current" ]] && marker=" ← current"
      echo "  $p$marker"
    done
  else
    echo "  (no profiles yet)"
  fi
  echo ""
}

cmd_test() {
  if [[ ! -f "$PROVIDER_CONFIG" ]]; then log "Not configured."; return 1; fi
  local target; target=$(_get_path)
  [[ -d "$target" ]] && log "Directory accessible: $target" || log "Directory NOT accessible: $target"
}

cmd_info() {
  if [[ -f "$PROVIDER_CONFIG" ]]; then
    echo "  Path: $(_get_path)"
    echo "  Profile: $(get_profile_name)"
  else echo "  Not configured"; fi
}

case "${1:-info}" in setup) cmd_setup;; push) cmd_push;; pull) cmd_pull;; test) cmd_test;; info) cmd_info;; list-profiles) cmd_list_profiles;; esac
