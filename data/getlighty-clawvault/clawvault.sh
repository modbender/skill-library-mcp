#!/usr/bin/env bash
# ClawVault — Main CLI
# Portable identity vault for OpenClaw
# Usage: clawvault.sh <command> [args]

set -euo pipefail

VERSION="3.0.0"
VAULT_DIR="$HOME/.clawvault"
CONFIG="$VAULT_DIR/config.yaml"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
PROVIDERS_DIR="$SCRIPT_DIR/providers"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[clawvault $(timestamp)] $*"; }

get_profile_name() {
  local name
  name=$(grep 'profile_name:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  echo "${name:-$(hostname -s 2>/dev/null || echo default)}"
}

detect_os() { case "$(uname -s)" in Darwin) echo "macos";; Linux) echo "linux";; *) echo "unknown";; esac; }
detect_openclaw_dir() {
  if [[ -d "$HOME/.openclaw" ]]; then echo "$HOME/.openclaw"
  elif [[ -d "$HOME/clawd" ]]; then echo "$HOME/clawd"
  else echo ""; fi
}

# ─── Init ─────────────────────────────────────────────────────

cmd_init() {
  if [[ -f "$CONFIG" ]]; then
    log "Already initialized at $VAULT_DIR"
    log "Run 'clawvault.sh status' or 'clawvault.sh provider setup <name>'"
    return 0
  fi

  log "Initializing ClawVault v$VERSION..."

  local os instance_id openclaw_dir
  os="$(detect_os)"
  instance_id="$(hostname -s 2>/dev/null || echo x)-$(date +%s | shasum -a 256 2>/dev/null | cut -c1-8 || echo $$)"
  openclaw_dir="$(detect_openclaw_dir)"

  mkdir -p "$VAULT_DIR"/{identity,knowledge,knowledge/projects,local}

  # Create config
  cat > "$CONFIG" <<YAML
# ClawVault Configuration v$VERSION
# Generated: $(timestamp)

vault:
  version: "$VERSION"
  instance_id: "$instance_id"
  profile_name: "$(hostname -s 2>/dev/null || echo default)"

system:
  os: "$os"
  hostname: "$(hostname -s 2>/dev/null || echo unknown)"
  openclaw_dir: "$openclaw_dir"

# Set by 'clawvault.sh provider setup <name>'
provider: ""

sync:
  interval_minutes: 5
  # What to auto-sync
  knowledge: true
  memory: true
  projects: true
  requirements: true
  skills_list: true
  config: false
  soul: false
  identity_md: false

packages:
  track:
    brew: true
    apt: true
    snap: true
    flatpak: true
    npm_global: true
    pip_global: true
YAML

  # Create instance registry
  cat > "$VAULT_DIR/identity/instances.yaml" <<YAML
# ClawVault Instance Registry
instances:
  - id: "$instance_id"
    hostname: "$(hostname -s 2>/dev/null || echo unknown)"
    os: "$os"
    openclaw_dir: "$openclaw_dir"
    registered: "$(timestamp)"
    last_sync: null
    soul_name: ""
YAML

  # Generate keypair
  bash "$SRC_DIR/keypair.sh" generate

  # Copy from openclaw if exists
  if [[ -n "$openclaw_dir" && -d "$openclaw_dir" ]]; then
    local ws="$openclaw_dir/workspace"
    [[ -f "$ws/USER.md" ]]     && cp "$ws/USER.md"     "$VAULT_DIR/identity/USER.md"     && log "  Imported USER.md"
    [[ -f "$ws/MEMORY.md" ]]   && cp "$ws/MEMORY.md"   "$VAULT_DIR/knowledge/MEMORY.md"  && log "  Imported MEMORY.md"
    [[ -f "$ws/SOUL.md" ]]     && cp "$ws/SOUL.md"     "$VAULT_DIR/local/SOUL.md"        && log "  Saved SOUL.md (local-only)"
    [[ -f "$ws/IDENTITY.md" ]] && cp "$ws/IDENTITY.md"  "$VAULT_DIR/local/IDENTITY.md"   && log "  Saved IDENTITY.md (local-only)"
    if [[ -d "$ws/memory/projects" ]]; then
      cp -r "$ws/memory/projects/"* "$VAULT_DIR/knowledge/projects/" 2>/dev/null && log "  Imported project context"
    fi
  fi

  # Initial package scan
  bash "$SRC_DIR/../track-packages.sh" scan 2>/dev/null || true

  # Initialize local git for history
  bash "$SRC_DIR/sync-engine.sh" status >/dev/null 2>&1 || true

  echo ""
  echo "🦞 ClawVault initialized!"
  echo ""
  local profile_name
  profile_name=$(get_profile_name)
  echo "  Instance:  $instance_id"
  echo "  Profile:   $profile_name"
  echo "  Vault:     $VAULT_DIR"
  echo "  OS:        $os"
  echo "  OpenClaw:  ${openclaw_dir:-not found}"
  echo ""
  echo "Next: pick a storage provider:"
  echo "  clawvault.sh provider setup cloud      ← managed, easiest"
  echo "  clawvault.sh provider setup gdrive     ← Google Drive"
  echo "  clawvault.sh provider setup dropbox    ← Dropbox"
  echo "  clawvault.sh provider setup git        ← any Git repo"
  echo "  clawvault.sh provider setup ftp        ← FTP/SFTP server"
  echo "  clawvault.sh provider setup s3         ← S3 bucket"
  echo "  clawvault.sh provider setup local      ← USB/NAS"
  echo ""
}

# ─── Status ───────────────────────────────────────────────────

cmd_status() {
  if [[ ! -f "$CONFIG" ]]; then
    echo "ClawVault not initialized. Run: clawvault.sh init"
    return 1
  fi

  bash "$SRC_DIR/sync-engine.sh" status

  # Provider details
  local provider
  provider=$(grep '^provider:' "$CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"')
  if [[ -n "$provider" && -f "$PROVIDERS_DIR/${provider}.sh" ]]; then
    echo "Provider Details"
    echo "━━━━━━━━━━━━━━━━"
    bash "$PROVIDERS_DIR/${provider}.sh" info
    echo ""
  fi
}

# ─── Cloud shortcut ───────────────────────────────────────────

cmd_cloud() {
  local subcmd="${1:-}"
  case "$subcmd" in
    signup|setup) bash "$SRC_DIR/provider.sh" setup cloud ;;
    usage)        bash "$PROVIDERS_DIR/cloud.sh" usage ;;
    *)            bash "$SRC_DIR/provider.sh" setup cloud ;;
  esac
}

# ─── Profile ─────────────────────────────────────────────────

cmd_profile() {
  if [[ ! -f "$CONFIG" ]]; then
    echo "ClawVault not initialized. Run: clawvault.sh init"
    return 1
  fi

  local subcmd="${1:-show}"
  case "$subcmd" in
    show)
      echo "Profile: $(get_profile_name)"
      ;;
    rename)
      local new_name="${2:-}"
      if [[ -z "$new_name" ]]; then
        echo "Usage: clawvault.sh profile rename <name>"
        return 1
      fi
      if [[ ! "$new_name" =~ ^[a-zA-Z0-9_-]{1,64}$ ]]; then
        echo "Invalid name. Use letters, numbers, dashes, underscores (max 64 chars)."
        return 1
      fi
      if [[ "$(uname -s)" == "Darwin" ]]; then
        sed -i '' "s/^  profile_name: .*/  profile_name: \"$new_name\"/" "$CONFIG"
      else
        sed -i "s/^  profile_name: .*/  profile_name: \"$new_name\"/" "$CONFIG"
      fi
      log "Profile renamed to: $new_name"
      ;;
    list)
      local provider
      provider=$(grep '^provider:' "$CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"')
      if [[ -z "$provider" || ! -f "$PROVIDERS_DIR/${provider}.sh" ]]; then
        echo "No provider configured."
        return 1
      fi
      CLAWVAULT_PROFILE="$(get_profile_name)" bash "$PROVIDERS_DIR/${provider}.sh" list-profiles
      ;;
    pull)
      local target="${2:-}"
      if [[ -z "$target" ]]; then
        echo "Usage: clawvault.sh profile pull <name>"
        echo "Use 'clawvault.sh profile list' to see available profiles."
        return 1
      fi
      log "Pulling profile: $target"
      CLAWVAULT_PROFILE="$target" bash "$SRC_DIR/sync-engine.sh" pull
      log "Restored profile: $target"
      ;;
    *)
      echo "Usage: clawvault.sh profile {show|rename|list|pull}"
      ;;
  esac
}

# ─── Help ─────────────────────────────────────────────────────

cmd_help() {
  echo ""
  echo "🦞 ClawVault v$VERSION — Portable Agent Environment"
  echo ""
  echo "Setup:"
  echo "  init                    Initialize vault on this machine"
  echo "  provider setup <name>   Configure storage (cloud/gdrive/dropbox/ftp/git/s3/local)"
  echo "  provider list           Show available providers"
  echo "  cloud signup            Quick setup for ClawVault Cloud"
  echo ""
  echo "Sync:"
  echo "  sync start              Start auto-sync (iCloud-like)"
  echo "  sync stop               Stop auto-sync"
  echo "  sync push               Force push now"
  echo "  sync pull               Force pull now"
  echo "  sync status             Show sync status"
  echo ""
  echo "History:"
  echo "  log                     Show vault commit history"
  echo "  diff                    Show pending changes"
  echo "  rollback                Revert to previous state"
  echo ""
  echo "Packages:"
  echo "  packages scan           Scan installed packages"
  echo "  packages diff           Compare local vs vault"
  echo "  packages install        Install missing from vault"
  echo ""
  echo "Migration:"
  echo "  migrate pull            Pull vault to this machine"
  echo "  migrate push-identity   Push SOUL/IDENTITY to vault (opt-in)"
  echo "  migrate status          Show migration status"
  echo ""
  echo "Keys:"
  echo "  key show                Show public key"
  echo "  key fingerprint         Show key fingerprint"
  echo "  key push                Push public key to vault"
  echo "  key rotate              Generate new keypair"
  echo "  key verify              Check keypair health"
  echo ""
  echo "Profiles:"
  echo "  profile show            Show current profile name"
  echo "  profile rename <name>   Rename this machine's profile"
  echo "  profile list            List all remote profiles"
  echo "  profile pull <name>     Restore from a specific profile"
  echo ""
  echo "Other:"
  echo "  status                  Full vault status"
  echo "  help                    This help"
  echo ""
}

# ─── Route Commands ───────────────────────────────────────────

case "${1:-help}" in
  init)      cmd_init ;;
  status)    cmd_status ;;
  help|-h)   cmd_help ;;

  # Provider
  provider)  bash "$SRC_DIR/provider.sh" "${2:-list}" "${3:-}" ;;
  cloud)     cmd_cloud "${2:-}" ;;

  # Sync
  sync)
    case "${2:-status}" in
      start)  bash "$SRC_DIR/sync-engine.sh" start ;;
      stop)   bash "$SRC_DIR/sync-engine.sh" stop ;;
      push)   bash "$SRC_DIR/sync-engine.sh" push ;;
      pull)   bash "$SRC_DIR/sync-engine.sh" pull ;;
      status) bash "$SRC_DIR/sync-engine.sh" status ;;
      *)      echo "Usage: clawvault.sh sync {start|stop|push|pull|status}" ;;
    esac ;;

  # History
  log)       bash "$SRC_DIR/sync-engine.sh" log ;;
  diff)      bash "$SRC_DIR/sync-engine.sh" diff ;;
  rollback)  bash "$SRC_DIR/sync-engine.sh" rollback ;;

  # Packages
  packages)  bash "$SCRIPT_DIR/track-packages.sh" "${2:-scan}" "${3:-}" ;;

  # Migration
  migrate)   bash "$SCRIPT_DIR/migrate.sh" "${2:-status}" ;;

  # Keys
  key)       bash "$SRC_DIR/keypair.sh" "${2:-show-public}" ;;

  # Profiles
  profile)   cmd_profile "${2:-show}" "${3:-}" ;;

  *)
    echo "Unknown command: $1"
    cmd_help
    exit 1 ;;
esac
