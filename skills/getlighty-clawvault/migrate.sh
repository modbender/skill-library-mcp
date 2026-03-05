#!/usr/bin/env bash
# ClawVault — Migration Wizard
# Interactive restore/migration for new machines
# Usage: migrate.sh {pull|push-identity|status}

set -euo pipefail

VAULT_DIR="$HOME/.clawvault"
CONFIG="$VAULT_DIR/config.yaml"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[clawvault:migrate $(timestamp)] $*"; }

# ─── Pull (restore to this machine) ─────────────────────────

cmd_pull() {
  if [[ ! -f "$CONFIG" ]]; then
    log "Vault not initialized. Run 'clawvault.sh init' first."
    return 1
  fi

  local provider
  provider=$(grep '^provider:' "$CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"')

  if [[ -z "$provider" ]]; then
    log "No provider configured. Run 'clawvault.sh provider setup <name>' first."
    return 1
  fi

  echo ""
  echo "ClawVault Migration — Pull"
  echo "=========================="
  echo ""
  echo "This will:"
  echo "  1. Pull knowledge from your vault ($provider)"
  echo "  2. Restore USER.md, MEMORY.md, and project context"
  echo "  3. Show package differences"
  echo "  4. Offer to install missing packages"
  echo ""
  echo "Your local SOUL.md and IDENTITY.md will NOT be overwritten."
  echo ""
  read -rp "Continue? [Y/n]: " yn
  if [[ "$yn" =~ ^[Nn] ]]; then
    log "Migration cancelled."
    return 0
  fi

  # Step 0: List available profiles and let user pick
  echo ""
  log "Checking available profiles..."
  local provider_script="$SCRIPT_DIR/providers/${provider}.sh"
  bash "$provider_script" list-profiles 2>/dev/null || echo "  (could not list profiles)"

  local profile_name
  profile_name=$(grep 'profile_name:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  profile_name="${profile_name:-$(hostname -s 2>/dev/null || echo default)}"
  read -rp "Profile to restore [$profile_name]: " chosen
  chosen="${chosen:-$profile_name}"

  # Step 1: Pull from provider
  echo ""
  log "Step 1/4: Pulling profile '$chosen' from $provider..."
  CLAWVAULT_PROFILE="$chosen" bash "$SCRIPT_DIR/src/sync-engine.sh" pull

  # Step 2: Show what was restored
  echo ""
  log "Step 2/4: Restored files:"
  [[ -f "$VAULT_DIR/identity/USER.md" ]]   && echo "  + identity/USER.md" || echo "  - identity/USER.md (not in vault)"
  [[ -f "$VAULT_DIR/knowledge/MEMORY.md" ]] && echo "  + knowledge/MEMORY.md" || echo "  - knowledge/MEMORY.md (not in vault)"

  local project_count=0
  if [[ -d "$VAULT_DIR/knowledge/projects" ]]; then
    project_count=$(find "$VAULT_DIR/knowledge/projects" -type f 2>/dev/null | wc -l | tr -d ' ')
  fi
  echo "  + $project_count project context file(s)"

  # Step 3: Register this instance
  echo ""
  log "Step 3/4: Registering this instance..."
  local instance_id hostname_str os_str
  instance_id=$(grep 'instance_id:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  hostname_str=$(hostname -s 2>/dev/null || echo "unknown")
  os_str=$(uname -s | tr '[:upper:]' '[:lower:]')
  [[ "$os_str" == "darwin" ]] && os_str="macos"

  if [[ -f "$VAULT_DIR/identity/instances.yaml" ]]; then
    if ! grep -q "$instance_id" "$VAULT_DIR/identity/instances.yaml" 2>/dev/null; then
      cat >> "$VAULT_DIR/identity/instances.yaml" <<YAML
  - id: "$instance_id"
    hostname: "$hostname_str"
    os: "$os_str"
    registered: "$(timestamp)"
    last_sync: null
    soul_name: ""
YAML
      log "  Registered as $instance_id"
    else
      log "  Already registered"
    fi
  fi

  # Step 4: Package diff
  echo ""
  log "Step 4/4: Checking packages..."
  if [[ -f "$VAULT_DIR/.vault-requirements.yaml" ]] || [[ -f "$VAULT_DIR/requirements.yaml" ]]; then
    # Scan local packages first
    bash "$SCRIPT_DIR/track-packages.sh" scan 2>/dev/null || true
    # If we pulled vault requirements, use them for diff
    [[ -f "$VAULT_DIR/requirements.yaml" ]] && cp "$VAULT_DIR/requirements.yaml" "$VAULT_DIR/.vault-requirements.yaml" 2>/dev/null || true
    bash "$SCRIPT_DIR/track-packages.sh" diff 2>/dev/null || true

    echo ""
    read -rp "Install missing packages? [y/N]: " yn
    if [[ "$yn" =~ ^[Yy] ]]; then
      bash "$SCRIPT_DIR/track-packages.sh" install
    fi
  else
    log "  No package requirements in vault"
  fi

  # Sync restored files to OpenClaw if present
  local openclaw_dir
  openclaw_dir=$(grep 'openclaw_dir:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  if [[ -n "$openclaw_dir" && -d "$openclaw_dir" ]]; then
    local ws="$openclaw_dir/workspace"
    mkdir -p "$ws"
    [[ -f "$VAULT_DIR/identity/USER.md" ]]   && cp "$VAULT_DIR/identity/USER.md"   "$ws/USER.md" 2>/dev/null && log "  Synced USER.md to OpenClaw"
    [[ -f "$VAULT_DIR/knowledge/MEMORY.md" ]] && cp "$VAULT_DIR/knowledge/MEMORY.md" "$ws/MEMORY.md" 2>/dev/null && log "  Synced MEMORY.md to OpenClaw"
  fi

  echo ""
  log "Migration complete!"
  echo ""
}

# ─── Push Identity (opt-in only) ────────────────────────────

cmd_push_identity() {
  if [[ ! -f "$CONFIG" ]]; then
    log "Vault not initialized."
    return 1
  fi

  echo ""
  echo "Push Local Identity to Vault"
  echo "============================"
  echo ""
  echo "This will push your LOCAL-ONLY files to the vault."
  echo "These files are normally per-machine and NOT synced."
  echo ""

  local has_soul=false has_identity=false
  [[ -f "$VAULT_DIR/local/SOUL.md" ]]     && has_soul=true
  [[ -f "$VAULT_DIR/local/IDENTITY.md" ]] && has_identity=true

  if ! $has_soul && ! $has_identity; then
    log "No SOUL.md or IDENTITY.md found in local/"
    return 0
  fi

  $has_soul     && echo "  SOUL.md     — $(wc -l < "$VAULT_DIR/local/SOUL.md" | tr -d ' ') lines"
  $has_identity && echo "  IDENTITY.md — $(wc -l < "$VAULT_DIR/local/IDENTITY.md" | tr -d ' ') lines"
  echo ""
  echo "WARNING: This will make these files available to ALL instances."
  echo "Other machines will need to explicitly pull them."
  echo ""
  read -rp "Push to vault? [y/N]: " yn

  if [[ ! "$yn" =~ ^[Yy] ]]; then
    log "Cancelled."
    return 0
  fi

  mkdir -p "$VAULT_DIR/identity/shared-souls"
  local hostname_str
  hostname_str=$(hostname -s 2>/dev/null || echo "unknown")

  $has_soul     && cp "$VAULT_DIR/local/SOUL.md"     "$VAULT_DIR/identity/shared-souls/SOUL-${hostname_str}.md" && log "  Pushed SOUL.md as SOUL-${hostname_str}.md"
  $has_identity && cp "$VAULT_DIR/local/IDENTITY.md"  "$VAULT_DIR/identity/shared-souls/IDENTITY-${hostname_str}.md" && log "  Pushed IDENTITY.md as IDENTITY-${hostname_str}.md"

  # Trigger sync
  bash "$SCRIPT_DIR/src/sync-engine.sh" push 2>/dev/null || log "Push to provider deferred"

  echo ""
  log "Identity pushed to vault (under identity/shared-souls/)"
}

# ─── Status ──────────────────────────────────────────────────

cmd_status() {
  if [[ ! -f "$CONFIG" ]]; then
    echo "ClawVault not initialized."
    return 1
  fi

  echo ""
  echo "Migration Status"
  echo "================"

  # Instance info
  local instance_id
  instance_id=$(grep 'instance_id:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  echo "  This instance: $instance_id"

  # Check what's populated
  echo ""
  echo "  Vault contents:"
  [[ -f "$VAULT_DIR/identity/USER.md" ]]    && echo "    + identity/USER.md"       || echo "    - identity/USER.md (empty)"
  [[ -f "$VAULT_DIR/knowledge/MEMORY.md" ]] && echo "    + knowledge/MEMORY.md"    || echo "    - knowledge/MEMORY.md (empty)"
  [[ -f "$VAULT_DIR/local/SOUL.md" ]]       && echo "    + local/SOUL.md"          || echo "    - local/SOUL.md (empty)"
  [[ -f "$VAULT_DIR/local/IDENTITY.md" ]]   && echo "    + local/IDENTITY.md"      || echo "    - local/IDENTITY.md (empty)"
  [[ -f "$VAULT_DIR/requirements.yaml" ]]   && echo "    + requirements.yaml"      || echo "    - requirements.yaml (no scan)"

  # Other instances
  if [[ -f "$VAULT_DIR/identity/instances.yaml" ]]; then
    local count
    count=$(grep -c '^\s*- id:' "$VAULT_DIR/identity/instances.yaml" 2>/dev/null || echo "0")
    echo ""
    echo "  Connected instances: $count"
    grep '^\s*- id:\|^\s*hostname:\|^\s*os:' "$VAULT_DIR/identity/instances.yaml" 2>/dev/null | while IFS= read -r line; do
      echo "    $line"
    done
  fi

  # Provider
  local provider
  provider=$(grep '^provider:' "$CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"')
  echo ""
  echo "  Provider: ${provider:-none}"
  echo ""
}

# ─── Main ────────────────────────────────────────────────────

case "${1:-status}" in
  pull)          cmd_pull ;;
  push-identity) cmd_push_identity ;;
  status)        cmd_status ;;
  *)             echo "Usage: migrate.sh {pull|push-identity|status}"; exit 1 ;;
esac
