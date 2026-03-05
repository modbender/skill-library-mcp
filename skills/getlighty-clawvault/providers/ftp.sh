#!/usr/bin/env bash
# ClawVault Provider — FTP / SFTP
set -euo pipefail
VAULT_DIR="$HOME/.clawvault"; CONFIG="$VAULT_DIR/config.yaml"; PROVIDER_CONFIG="$VAULT_DIR/.provider-ftp.json"
timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }; log() { echo "[clawvault:ftp $(timestamp)] $*"; }
EXCLUDE="--exclude local/ --exclude keys/ --exclude .provider-*.json --exclude .cloud-provider.json --exclude .sync-* --exclude .pull-* --exclude .heartbeat.pid --exclude .git-local/"

get_profile_name() {
  if [[ -n "${CLAWVAULT_PROFILE:-}" ]]; then echo "$CLAWVAULT_PROFILE"; return; fi
  local name
  name=$(grep 'profile_name:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  echo "${name:-$(hostname -s 2>/dev/null || echo default)}"
}

cmd_setup() {
  echo ""; echo "🔗 FTP/SFTP Setup"; echo "━━━━━━━━━━━━━━━━━"
  read -rp "Protocol [sftp]: " proto; proto="${proto:-sftp}"
  read -rp "Host: " host; read -rp "Port [22]: " port; port="${port:-22}"
  read -rp "Username: " user; read -rp "Remote path [/clawvault]: " rpath; rpath="${rpath:-/clawvault}"
  echo ""
  echo "Authentication: your ClawVault Ed25519 key will be used."
  echo "Add this public key to your server's authorized_keys:"
  echo "────────────────────────────────"
  cat "$VAULT_DIR/keys/clawvault_ed25519.pub" 2>/dev/null
  echo "────────────────────────────────"

  cat > "$PROVIDER_CONFIG" <<JSON
{"provider":"ftp","protocol":"$proto","host":"$host","port":$port,"user":"$user","path":"$rpath","configured":"$(timestamp)"}
JSON
  log "✓ ${proto^^} configured → $user@$host:$rpath"
}

_load() {
  proto=$(python3 -c "import json;d=json.load(open('$PROVIDER_CONFIG'));print(d['protocol'])" 2>/dev/null)
  host=$(python3 -c "import json;d=json.load(open('$PROVIDER_CONFIG'));print(d['host'])" 2>/dev/null)
  port=$(python3 -c "import json;d=json.load(open('$PROVIDER_CONFIG'));print(d['port'])" 2>/dev/null)
  user=$(python3 -c "import json;d=json.load(open('$PROVIDER_CONFIG'));print(d['user'])" 2>/dev/null)
  rpath=$(python3 -c "import json;d=json.load(open('$PROVIDER_CONFIG'));print(d['path'])" 2>/dev/null)
}

cmd_push() {
  _load; local key="$VAULT_DIR/keys/clawvault_ed25519"
  local profile_name; profile_name=$(get_profile_name)
  local target_path="$rpath/profiles/$profile_name"
  ssh -i "$key" -p "$port" -o StrictHostKeyChecking=no "$user@$host" "mkdir -p '$target_path'" 2>/dev/null || true
  log "Pushing via $proto to $host (profile: $profile_name)..."
  rsync -avz -e "ssh -i $key -p $port -o StrictHostKeyChecking=no" \
    $EXCLUDE "$VAULT_DIR/" "$user@$host:$target_path/" 2>&1 | tail -3
  log "Push complete (profile: $profile_name)"
}

cmd_pull() {
  _load; local key="$VAULT_DIR/keys/clawvault_ed25519"
  local d="$VAULT_DIR/.pull-ftp"; mkdir -p "$d"
  local profile_name; profile_name=$(get_profile_name)
  local source_path="$rpath/profiles/$profile_name"
  # Fallback to root if profiles/ doesn't exist
  if ! ssh -i "$key" -p "$port" -o StrictHostKeyChecking=no "$user@$host" "ls '$rpath/profiles'" &>/dev/null; then
    source_path="$rpath"
    log "No profiles found, falling back to root..."
  fi
  log "Pulling via $proto from $host (profile: $profile_name)..."
  rsync -avz -e "ssh -i $key -p $port -o StrictHostKeyChecking=no" \
    --exclude local/ "$user@$host:$source_path/" "$d/" 2>&1 | tail -3
  for f in identity/USER.md knowledge/MEMORY.md requirements.yaml manifest.json identity/instances.yaml; do
    [[ -f "$d/$f" ]] && mkdir -p "$(dirname "$VAULT_DIR/$f")" && cp "$d/$f" "$VAULT_DIR/$f"
  done
  [[ -d "$d/knowledge/projects" ]] && mkdir -p "$VAULT_DIR/knowledge/projects" && cp -r "$d/knowledge/projects/"* "$VAULT_DIR/knowledge/projects/" 2>/dev/null || true
  rm -rf "$d"; log "Pull complete (profile: $profile_name)"
}

cmd_test() {
  _load; local key="$VAULT_DIR/keys/clawvault_ed25519"
  ssh -i "$key" -p "$port" -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$user@$host" "ls $rpath" &>/dev/null \
    && log "✓ Connected to $host" || log "✗ Connection failed"
}

cmd_list_profiles() {
  if [[ ! -f "$PROVIDER_CONFIG" ]]; then log "Not configured."; return 1; fi
  _load; local key="$VAULT_DIR/keys/clawvault_ed25519"
  local current; current=$(get_profile_name)
  echo ""; echo "Remote Profiles"; echo "==============="
  if ssh -i "$key" -p "$port" -o StrictHostKeyChecking=no "$user@$host" "ls '$rpath/profiles'" &>/dev/null; then
    ssh -i "$key" -p "$port" -o StrictHostKeyChecking=no "$user@$host" "ls '$rpath/profiles/'" 2>/dev/null | while read -r p; do
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
    _load
    echo "  Remote: $proto://$user@$host:$port$rpath"
    echo "  Profile: $(get_profile_name)"
  else echo "  Not configured"; fi
}

case "${1:-info}" in setup) cmd_setup;; push) cmd_push;; pull) cmd_pull;; test) cmd_test;; info) cmd_info;; list-profiles) cmd_list_profiles;; esac
