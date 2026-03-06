#!/usr/bin/env bash
set -euo pipefail

# agent-security-ops: Cron-friendly monitoring (delta detection)
# MARKER:agent-security-ops
# Exit 0 = clean/no new findings | Exit 1 = new findings

SCRIPT_VERSION="1.1.0"

export PATH="$HOME/.local/bin:$PATH"

if [ -t 2 ]; then
  GREEN='\033[0;32m'; YELLOW='\033[0;33m'; BLUE='\033[0;34m'; NC='\033[0m'; BOLD='\033[1m'
else
  GREEN=''; YELLOW=''; BLUE=''; NC=''; BOLD=''
fi

log()  { printf "${GREEN}✓${NC} %s\n" "$1" >&2; }
warn() { printf "${YELLOW}⚠${NC} %s\n" "$1" >&2; }
info() { printf "${BLUE}→${NC} %s\n" "$1" >&2; }

# Parse flags
for arg in "$@"; do
  case "$arg" in
    --help|-h)
      cat >&2 <<'USAGE'
Usage: monitor.sh [OPTIONS] [/path/to/repo]

Cron-friendly delta detection. Exits 1 on changes, 0 if unchanged.
Creates .security-ops/ in the repo for state files (add to .gitignore).

Options:
  --help, -h    Show this help
  --version     Show version
USAGE
      exit 0
      ;;
    --version)
      echo "agent-security-ops monitor.sh v${SCRIPT_VERSION}" >&2
      exit 0
      ;;
  esac
done

REPO="${1:-.}"
REPO="$(cd "$REPO" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

STATE_DIR="$REPO/.security-ops"
LAST_SCAN="$STATE_DIR/last-scan.json"
LAST_HASH="$STATE_DIR/last-scan.hash"
LOCK_FILE="$STATE_DIR/monitor.lock"
mkdir -p "$STATE_DIR"

# [M2] flock-based locking to prevent concurrent runs
if command -v flock >/dev/null 2>&1; then
  exec 9>"$LOCK_FILE"
  if ! flock -n 9; then
    warn "Another monitor.sh instance is running (locked). Exiting."
    exit 0
  fi
else
  # macOS doesn't have flock — use mkdir-based lock
  if ! mkdir "$LOCK_FILE.d" 2>/dev/null; then
    # Check if stale (older than 10 minutes)
    if [ -d "$LOCK_FILE.d" ]; then
      lock_mtime=$(stat -f %m "$LOCK_FILE.d" 2>/dev/null || stat -c %Y "$LOCK_FILE.d" 2>/dev/null || echo 0)
      lock_age=$(( $(date +%s) - lock_mtime ))
      if [ "$lock_age" -gt 600 ]; then
        warn "Removing stale lock (${lock_age}s old)"
        rmdir "$LOCK_FILE.d" 2>/dev/null || true
        mkdir "$LOCK_FILE.d" 2>/dev/null || { warn "Lock contention. Exiting."; exit 0; }
      else
        warn "Another monitor.sh instance is running. Exiting."
        exit 0
      fi
    fi
  fi
  USING_MKDIR_LOCK=1
  trap 'rmdir "$LOCK_FILE.d" 2>/dev/null || true' EXIT
fi

info "Running security scan on $REPO..."

# [M2] Use mktemp for temp files
SCAN_TMP=$(mktemp)
cleanup() { rm -f "$SCAN_TMP"; [ "${USING_MKDIR_LOCK:-0}" = "1" ] && rmdir "$LOCK_FILE.d" 2>/dev/null || true; }
trap cleanup EXIT

"$SCRIPT_DIR/scan.sh" "$REPO" > "$SCAN_TMP"
current_scan=$(cat "$SCAN_TMP")

# Content-based delta: hash findings, stripping volatile fields
current_hash=$(echo "$current_scan" | grep -v '"timestamp"' | grep -v '"listeners"' | shasum -a 256 | cut -d' ' -f1)

if [ -f "$LAST_HASH" ]; then
  last_hash=$(cat "$LAST_HASH" 2>/dev/null || echo "")

  if [ "$current_hash" != "$last_hash" ]; then
    warn "Scan results changed (hash mismatch)"
    # Atomic writes via mktemp + mv
    tmp_scan=$(mktemp "$STATE_DIR/.last-scan.XXXXXX")
    echo "$current_scan" > "$tmp_scan"
    mv "$tmp_scan" "$LAST_SCAN"
    tmp_hash=$(mktemp "$STATE_DIR/.last-hash.XXXXXX")
    echo "$current_hash" > "$tmp_hash"
    mv "$tmp_hash" "$LAST_HASH"
    echo "$current_scan"
    exit 1
  else
    log "No change (hash match)"
  fi
else
  info "First scan — establishing baseline"
  current_total=$(echo "$current_scan" | grep -o '"total_findings": *[0-9]*' | grep -o '[0-9]*$' || echo 0)
  if [ "${current_total:-0}" -gt 0 ]; then
    warn "Baseline has $current_total finding(s)"
  else
    log "Baseline clean"
  fi
fi

# Atomic state writes
tmp_scan=$(mktemp "$STATE_DIR/.last-scan.XXXXXX")
echo "$current_scan" > "$tmp_scan"
mv "$tmp_scan" "$LAST_SCAN"
tmp_hash=$(mktemp "$STATE_DIR/.last-hash.XXXXXX")
echo "$current_hash" > "$tmp_hash"
mv "$tmp_hash" "$LAST_HASH"

echo "$current_scan"
exit 0
