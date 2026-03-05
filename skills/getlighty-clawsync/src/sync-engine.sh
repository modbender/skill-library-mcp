#!/usr/bin/env bash
# ClawSync — Sync Engine
# iCloud-like auto-sync: watches for changes, auto-commits to local git,
# auto-pushes to provider. Full history with rollback.
# Usage: sync-engine.sh {start|stop|push|pull|log|diff|rollback|status}

set -euo pipefail

VAULT_DIR="$HOME/.clawsync"
CONFIG="$VAULT_DIR/config.yaml"
SYNC_LOG="$VAULT_DIR/sync.log"
PID_FILE="$VAULT_DIR/.sync-engine.pid"
PROVIDERS_DIR="$(cd "$(dirname "$0")" && pwd)/../providers"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() {
  local msg
  msg="[sync-engine $(timestamp)] $*"
  echo "$msg"
  echo "$msg" >> "$SYNC_LOG" 2>/dev/null || true
}

get_provider() {
  grep '^provider:' "$CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"'
}

get_sync_interval() {
  grep 'interval_minutes:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"'
}

get_profile_name() {
  if [[ -n "${CLAWSYNC_PROFILE:-}" ]]; then echo "$CLAWSYNC_PROFILE"; return; fi
  local name
  name=$(grep 'profile_name:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  echo "${name:-$(hostname -s 2>/dev/null || echo default)}"
}

# ─── Local Git (version history) ─────────────────────────────
# Every change is committed locally before pushing to the provider.
# This gives us: full history, rollback, diff, and conflict detection.

init_local_git() {
  if [[ ! -d "$VAULT_DIR/.git" ]]; then
    git -C "$VAULT_DIR" init --quiet
    # Ignore non-syncable files
    cat > "$VAULT_DIR/.gitignore" <<'EOF'
local/
keys/
.provider-*.json
.cloud-provider.json
.sync-*
.pull-*
.heartbeat.pid
.git-local/
.git-remote/
*.pid
*.enc
sync.log
heartbeat.log
EOF
    git -C "$VAULT_DIR" add -A
    git -C "$VAULT_DIR" commit -m "vault initialized" --quiet 2>/dev/null || true
    log "Local git history initialized"
  fi
}

# Auto-commit any pending changes
auto_commit() {
  init_local_git

  cd "$VAULT_DIR"
  git add -A 2>/dev/null

  if git diff --cached --quiet 2>/dev/null; then
    return 1  # no changes
  fi

  # Build commit message from changed files
  local changed
  changed=$(git diff --cached --name-only 2>/dev/null | head -5 | tr '\n' ', ' | sed 's/,$//')
  local hostname_str
  hostname_str=$(hostname -s 2>/dev/null || echo "unknown")

  git commit -m "auto: $changed" \
    --author="clawsync <vault@${hostname_str}>" \
    --quiet 2>/dev/null

  log "Committed: $changed"
  return 0
}

# ─── Push to Provider ─────────────────────────────────────────

do_push() {
  local provider
  provider=$(get_provider)

  if [[ -z "$provider" ]]; then
    log "No provider configured."
    return 1
  fi

  # First, pull from openclaw workspace to vault
  sync_from_openclaw

  # Auto-commit local changes
  auto_commit || true

  # Update manifest
  update_manifest

  # Commit manifest update
  auto_commit || true

  # Push to provider (with profile)
  local profile_name
  profile_name=$(get_profile_name)
  local provider_script="$PROVIDERS_DIR/${provider}.sh"
  if [[ -f "$provider_script" ]]; then
    CLAWSYNC_PROFILE="$profile_name" bash "$provider_script" push
    log "✓ Pushed to $provider (profile: $profile_name)"
  else
    log "Provider script not found: $provider"
    return 1
  fi
}

# ─── Pull from Provider ──────────────────────────────────────

do_pull() {
  local provider
  provider=$(get_provider)

  if [[ -z "$provider" ]]; then
    log "No provider configured."
    return 1
  fi

  local profile_name
  profile_name=$(get_profile_name)
  local provider_script="$PROVIDERS_DIR/${provider}.sh"
  if [[ -f "$provider_script" ]]; then
    CLAWSYNC_PROFILE="$profile_name" bash "$provider_script" pull
    auto_commit || true
    sync_to_openclaw
    log "✓ Pulled from $provider (profile: $profile_name)"
  fi
}

# ─── Sync OpenClaw ↔ Vault ───────────────────────────────────

sync_from_openclaw() {
  local openclaw_dir
  openclaw_dir=$(grep 'openclaw_dir:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')

  if [[ -z "$openclaw_dir" || ! -d "$openclaw_dir" ]]; then
    return 0
  fi

  # Mirror entire openclaw directory into vault (excluding .git and runtime files)
  mkdir -p "$VAULT_DIR/openclaw"
  rsync -a --delete \
    --exclude '.git/' \
    --exclude 'node_modules/' \
    --exclude '*.swp' \
    --exclude '*.swo' \
    "$openclaw_dir/" "$VAULT_DIR/openclaw/" 2>/dev/null || true
}

sync_to_openclaw() {
  local openclaw_dir
  openclaw_dir=$(grep 'openclaw_dir:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')

  if [[ -z "$openclaw_dir" || ! -d "$openclaw_dir" ]]; then
    return 0
  fi

  # Mirror vault's openclaw copy back to the actual openclaw directory
  if [[ -d "$VAULT_DIR/openclaw" ]]; then
    rsync -a \
      --exclude '.git/' \
      --exclude 'node_modules/' \
      "$VAULT_DIR/openclaw/" "$openclaw_dir/" 2>/dev/null || true
  fi
}

# ─── Manifest ─────────────────────────────────────────────────

update_manifest() {
  local instance_id
  instance_id=$(grep 'instance_id:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')

  local is_macos=false
  [[ "$(uname -s)" == "Darwin" ]] && is_macos=true

  local files_json
  files_json=$(find "$VAULT_DIR" -maxdepth 3 -type f \
    -not -path '*/.git/*' \
    -not -path '*/local/*' \
    -not -path '*/keys/*' \
    -not -path '*/.provider-*' \
    -not -path '*/.cloud-*' \
    -not -path '*/.sync-*' \
    -not -path '*/.pull-*' \
    -not -name '*.pid' \
    -not -name '*.log' \
    -not -name 'manifest.json' | while read -r f; do
    local rel="${f#$VAULT_DIR/}"
    local sz
    sz=$(wc -c < "$f" 2>/dev/null | tr -d ' ')
    local modified="unknown"
    if $is_macos; then
      local epoch
      epoch=$(stat -f "%m" "$f" 2>/dev/null)
      [[ -n "$epoch" ]] && modified=$(date -r "$epoch" -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")
    else
      modified=$(date -r "$f" -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")
    fi
    echo "    \"$rel\": {\"size\": $sz, \"modified\": \"$modified\"},"
  done | sed '$ s/,$//')

  cat > "$VAULT_DIR/manifest.json" <<JSON
{
  "version": "2.0.0",
  "last_sync": "$(timestamp)",
  "synced_by": "$instance_id",
  "hostname": "$(hostname -s 2>/dev/null || echo unknown)",
  "provider": "$(get_provider)",
  "files": {
$files_json
  }
}
JSON
}

# ─── File Watcher (iCloud-like) ──────────────────────────────

cmd_start() {
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    log "Sync engine already running (PID $(cat "$PID_FILE"))"
    return 0
  fi

  init_local_git

  local interval
  interval=$(get_sync_interval)
  interval="${interval:-5}"
  local interval_sec=$((interval * 60))

  log "Starting sync engine (interval: ${interval}m)..."

  # Check if fswatch is available for real-time file watching
  if command -v fswatch &>/dev/null; then
    log "Using fswatch for real-time sync"
    (
      # Debounced fswatch: collect changes for 30 seconds, then sync
      fswatch -r -l 30 \
        --exclude '\.git' \
        --exclude 'local/' \
        --exclude 'keys/' \
        --exclude '\.sync-' \
        --exclude '\.pull-' \
        --exclude '\.pid' \
        --exclude '\.log' \
        "$VAULT_DIR/identity" "$VAULT_DIR/knowledge" "$VAULT_DIR/requirements.yaml" 2>/dev/null | \
      while read -r _; do
        do_push 2>/dev/null || log "Push failed, will retry"
      done
    ) &
    echo $! > "$PID_FILE"
  else
    # Fallback: polling at interval
    log "fswatch not found — using polling (install fswatch for real-time sync)"
    (
      while true; do
        do_push 2>/dev/null || log "Push failed, will retry"
        sleep "$interval_sec"
      done
    ) &
    echo $! > "$PID_FILE"
  fi

  log "✓ Sync engine started (PID $(cat "$PID_FILE"))"
}

cmd_stop() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid=$(cat "$PID_FILE")
    # Kill the process group (catches fswatch + subshells)
    kill -- -"$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    pkill -P "$pid" 2>/dev/null || true
    # Also kill any orphaned fswatch watching our vault
    pkill -f "fswatch.*clawsync" 2>/dev/null || true
    rm -f "$PID_FILE"
    log "✓ Sync engine stopped"
  else
    # Clean up orphans even without PID file
    pkill -f "fswatch.*clawsync" 2>/dev/null || true
    log "Not running"
  fi
}

# ─── History / Rollback ──────────────────────────────────────

cmd_log() {
  init_local_git
  echo ""
  echo "Vault History"
  echo "━━━━━━━━━━━━━"
  git -C "$VAULT_DIR" log --oneline --graph --decorate -20 2>/dev/null || echo "No history yet"
  echo ""
}

cmd_diff() {
  init_local_git
  local changes
  changes=$(git -C "$VAULT_DIR" status --short 2>/dev/null)
  if [[ -z "$changes" ]]; then
    echo "No pending changes"
  else
    echo ""
    echo "Pending Changes"
    echo "━━━━━━━━━━━━━━━"
    echo "$changes"
    echo ""
    git -C "$VAULT_DIR" diff 2>/dev/null | head -50
  fi
}

cmd_rollback() {
  init_local_git
  echo ""
  echo "Recent commits:"
  git -C "$VAULT_DIR" log --oneline -10 2>/dev/null
  echo ""
  read -rp "Rollback to commit (hash): " commit_hash
  if [[ -z "$commit_hash" ]]; then
    log "No commit specified."
    return 1
  fi

  echo "⚠ This will revert vault to commit $commit_hash"
  read -rp "Continue? [y/N]: " yn
  if [[ "$yn" =~ ^[Yy] ]]; then
    git -C "$VAULT_DIR" checkout "$commit_hash" -- . 2>/dev/null
    git -C "$VAULT_DIR" add -A
    git -C "$VAULT_DIR" commit -m "rollback to $commit_hash" --quiet 2>/dev/null
    log "✓ Rolled back to $commit_hash"
    echo "Run 'sync-engine.sh push' to propagate the rollback."
  fi
}

# ─── Status ───────────────────────────────────────────────────

cmd_status() {
  init_local_git
  echo ""
  echo "🔄 Sync Engine Status"
  echo "━━━━━━━━━━━━━━━━━━━━━"

  # Running?
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "  Engine:    RUNNING (PID $(cat "$PID_FILE"))"
    command -v fswatch &>/dev/null && echo "  Mode:      Real-time (fswatch)" || echo "  Mode:      Polling"
  else
    echo "  Engine:    STOPPED"
  fi

  # Profile
  local profile_name
  profile_name=$(get_profile_name)
  echo "  Profile:   $profile_name"

  # Provider
  local provider
  provider=$(get_provider)
  echo "  Provider:  ${provider:-none}"

  # Interval
  local interval
  interval=$(get_sync_interval)
  echo "  Interval:  ${interval:-5}m"

  # Last sync
  if [[ -f "$SYNC_LOG" ]]; then
    local last
    last=$(grep -E "Pushed to|Pulled from" "$SYNC_LOG" 2>/dev/null | tail -1 || true)
    echo "  Last sync: ${last:-never}"
  fi

  # Pending changes
  local pending
  pending=$(git -C "$VAULT_DIR" status --short 2>/dev/null | wc -l | tr -d ' ' || echo "0")
  echo "  Pending:   $pending file(s)"

  # History
  local commits
  commits=$(git -C "$VAULT_DIR" rev-list --count HEAD 2>/dev/null || echo "0")
  echo "  History:   $commits commits"

  # Vault size
  local size
  size=$(du -sh "$VAULT_DIR" 2>/dev/null | awk '{print $1}')
  echo "  Vault size: $size"
  echo ""
}

# ─── Main ─────────────────────────────────────────────────────

case "${1:-status}" in
  start)    cmd_start ;;
  stop)     cmd_stop ;;
  push)     do_push ;;
  pull)     do_pull ;;
  log)      cmd_log ;;
  diff)     cmd_diff ;;
  rollback) cmd_rollback ;;
  status)   cmd_status ;;
  *)        echo "Usage: sync-engine.sh {start|stop|push|pull|log|diff|rollback|status}"; exit 1 ;;
esac
