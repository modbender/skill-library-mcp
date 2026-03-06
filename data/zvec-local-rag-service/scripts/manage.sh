#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RUNTIME_DIR="$SKILL_DIR/.runtime"
LOG_DIR="$RUNTIME_DIR/logs"
PID_FILE="$RUNTIME_DIR/service.pid"

RAG_HOST="${RAG_HOST:-127.0.0.1}"
RAG_PORT="${RAG_PORT:-8787}"
OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
OLLAMA_EMBED_MODEL="${OLLAMA_EMBED_MODEL:-mxbai-embed-large}"
RAG_BASE_DIR="${RAG_BASE_DIR:-$HOME/.openclaw/data/zvec-rag-service}"
RAG_BASE_URL="${RAG_BASE_URL:-http://${RAG_HOST}:${RAG_PORT}}"

PLIST_PATH="$HOME/Library/LaunchAgents/com.openclaw.zvec-rag-service.plist"
LABEL="com.openclaw.zvec-rag-service"

pretty_json() { if command -v jq >/dev/null 2>&1; then jq .; else cat; fi; }
ensure_dirs() { mkdir -p "$RUNTIME_DIR" "$LOG_DIR" "$RAG_BASE_DIR"; }

ensure_deps() {
  ensure_dirs
  if [ ! -f "$SKILL_DIR/package.json" ]; then
    echo "Missing package.json in skill directory" >&2
    exit 1
  fi

  # Explicit dependency install (declared in skill metadata)
  if [ ! -d "$SKILL_DIR/node_modules/@zvec/zvec" ]; then
    npm install --prefix "$SKILL_DIR"
  fi
}

is_running() { [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; }

start_manual() {
  ensure_deps
  if is_running; then echo "Service already running (pid $(cat "$PID_FILE"))"; return; fi
  nohup env \
    RAG_HOST="$RAG_HOST" \
    RAG_PORT="$RAG_PORT" \
    OLLAMA_URL="$OLLAMA_URL" \
    OLLAMA_EMBED_MODEL="$OLLAMA_EMBED_MODEL" \
    RAG_BASE_DIR="$RAG_BASE_DIR" \
    node "$SCRIPT_DIR/rag-service.mjs" \
    > "$LOG_DIR/service.log" 2> "$LOG_DIR/service.err.log" &
  echo $! > "$PID_FILE"
  sleep 1
  echo "Started service pid $(cat "$PID_FILE")"
}

stop_manual() {
  if is_running; then kill "$(cat "$PID_FILE")"; rm -f "$PID_FILE"; echo "Stopped service"; else echo "Service is not running"; fi
}

write_plist() {
  mkdir -p "$HOME/Library/LaunchAgents"
  sed \
    -e "s|__NODE__|$(command -v node)|g" \
    -e "s|__SERVICE__|$SCRIPT_DIR/rag-service.mjs|g" \
    -e "s|__WORKDIR__|$SKILL_DIR|g" \
    -e "s|__OUT__|$LOG_DIR/service.log|g" \
    -e "s|__ERR__|$LOG_DIR/service.err.log|g" \
    -e "s|__RAG_HOST__|$RAG_HOST|g" \
    -e "s|__RAG_PORT__|$RAG_PORT|g" \
    -e "s|__OLLAMA_URL__|$OLLAMA_URL|g" \
    -e "s|__OLLAMA_EMBED_MODEL__|$OLLAMA_EMBED_MODEL|g" \
    -e "s|__RAG_BASE_DIR__|$RAG_BASE_DIR|g" \
    "$SKILL_DIR/references/launchd.plist.template" > "$PLIST_PATH"
}

launchd_start() { write_plist; launchctl bootout gui/$(id -u) "$PLIST_PATH" 2>/dev/null || true; launchctl bootstrap gui/$(id -u) "$PLIST_PATH"; launchctl kickstart -k gui/$(id -u)/$LABEL; }
launchd_stop() { launchctl bootout gui/$(id -u) "$PLIST_PATH" 2>/dev/null || true; }

case "${1:-}" in
  bootstrap) ensure_deps; echo "Bootstrap OK" ;;
  start) if [ "$(uname -s)" = "Darwin" ]; then launchd_start; else start_manual; fi ;;
  stop) if [ "$(uname -s)" = "Darwin" ]; then launchd_stop; else stop_manual; fi ;;
  restart) if [ "$(uname -s)" = "Darwin" ]; then launchd_stop; launchd_start; else stop_manual; start_manual; fi ;;
  status) if [ "$(uname -s)" = "Darwin" ]; then launchctl print gui/$(id -u)/$LABEL | head -n 80; else is_running && echo running || echo stopped; fi ;;
  health) curl -s "$RAG_BASE_URL/health" | pretty_json ;;
  ingest) dir="${2:-./docs}"; curl -s -X POST "$RAG_BASE_URL/ingest" -H 'Content-Type: application/json' -d "$(printf '{"dir":"%s","reset":true}' "$dir")" | pretty_json ;;
  search) shift; q="${*:-local semantic search}"; curl -s -X POST "$RAG_BASE_URL/search" -H 'Content-Type: application/json' -d "$(printf '{"query":"%s","topk":5}' "$q")" | pretty_json ;;
  install-launchd) ensure_deps; write_plist; echo "Wrote: $PLIST_PATH"; echo "Inspect it, then run: $0 start" ;;
  uninstall-launchd) launchd_stop; rm -f "$PLIST_PATH"; echo "Removed: $PLIST_PATH" ;;
  *) echo "Usage: $0 {bootstrap|start|stop|restart|status|health|ingest <dir>|search <query>|install-launchd|uninstall-launchd}"; exit 1 ;;
esac
