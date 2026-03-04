#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_ROOT="$(cd "$SKILL_DIR/.." && pwd)"
ENV_FILE="${OPENCLAW_DISPATCH_ENV:-$SKILLS_ROOT/dispatch.env.local}"

ALLOWED_KEYS=(RESULTS_BASE TMUX_SOCKET_DIR)

load_env_file() {
  local file="$1"
  [[ -f "$file" ]] || return 0

  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line//[[:space:]]/}" ]] && continue
    [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] || continue

    local key="${line%%=*}"
    local val="${line#*=}"
    key="$(echo "$key" | tr -d '[:space:]')"
    val="${val#"${val%%[![:space:]]*}"}"

    if [[ "$val" =~ ^\".*\"$ ]]; then val="${val:1:-1}"; fi
    if [[ "$val" =~ ^\'.*\'$ ]]; then val="${val:1:-1}"; fi

    case " ${ALLOWED_KEYS[*]} " in
      *" $key "*) export "$key=$val" ;;
      *) ;;
    esac
  done < "$file"
}

load_env_file "$ENV_FILE"

RESULTS_BASE="${RESULTS_BASE:-/home/miniade/clawd/data/claude-code-results}"
SOCKET_DIR="${TMUX_SOCKET_DIR:-/tmp/clawdbot-tmux-sockets}"

if [[ $# -ne 1 ]]; then
  echo "Usage: /cancel <run-id>" >&2
  exit 2
fi

RUN_ID="$1"
TARGET_DIR=""

if [[ "$RUN_ID" == */* ]]; then
  CANDIDATE="$RESULTS_BASE/$RUN_ID"
  [[ -d "$CANDIDATE" ]] && TARGET_DIR="$CANDIDATE"
else
  mapfile -t MATCHES < <(find "$RESULTS_BASE" -mindepth 2 -maxdepth 2 -type d -name "$RUN_ID" 2>/dev/null | sort)
  if [[ ${#MATCHES[@]} -eq 1 ]]; then
    TARGET_DIR="${MATCHES[0]}"
  elif [[ ${#MATCHES[@]} -gt 1 ]]; then
    echo "Error: run-id is ambiguous. Use <project>/<run-id>. Matches:" >&2
    printf '%s\n' "${MATCHES[@]}" >&2
    exit 2
  fi
fi

if [[ -z "$TARGET_DIR" || ! -d "$TARGET_DIR" ]]; then
  echo "Error: run-id not found: $RUN_ID" >&2
  exit 2
fi

META="$TARGET_DIR/task-meta.json"
if [[ ! -f "$META" ]]; then
  echo "Error: task-meta.json not found in $TARGET_DIR" >&2
  exit 2
fi

TMUX_SESSION=$(jq -r '.tmux_session // ""' "$META")
TMUX_SOCKET_NAME=$(jq -r '.tmux_socket_name // ""' "$META")
if [[ -z "$TMUX_SESSION" || -z "$TMUX_SOCKET_NAME" ]]; then
  echo "Error: tmux metadata missing in task-meta.json" >&2
  exit 2
fi

SOCKET_PATH="$SOCKET_DIR/$TMUX_SOCKET_NAME"
TARGET="${TMUX_SESSION}:0.0"

if ! command -v tmux >/dev/null 2>&1; then
  echo "Error: tmux not installed" >&2
  exit 2
fi

set +e
tmux -S "$SOCKET_PATH" send-keys -t "$TARGET" -l -- "/ralph-loop:cancel-ralph"
tmux -S "$SOCKET_PATH" send-keys -t "$TARGET" Enter
sleep 1
tmux -S "$SOCKET_PATH" send-keys -t "$TARGET" -l -- "/exit"
tmux -S "$SOCKET_PATH" send-keys -t "$TARGET" Enter
sleep 2
tmux -S "$SOCKET_PATH" kill-session -t "$TMUX_SESSION"
set -e

jq --arg ts "$(date -Iseconds)" '. + {status:"cancelled", completed_at:$ts, exit_code:130}' "$META" > "$META.tmp" && mv "$META.tmp" "$META"

echo "CANCEL_SENT run_id=$RUN_ID result_dir=$TARGET_DIR"
