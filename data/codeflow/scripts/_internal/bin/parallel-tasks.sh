#!/bin/bash
# parallel-tasks.sh — Run multiple Codeflow sessions across git worktrees
#
# Usage: ./parallel-tasks.sh [options] <tasks-file>
#
# Tasks file format (one task per line):
#   <working-dir> | <prompt>
#   ~/projects/api | Build user authentication
#   ~/projects/web | Add dark mode toggle
#
# Lines starting with # are ignored. Empty lines are ignored.
#
# Options:
#   -t <sec>       Timeout per task (default: 1800)
#   -a <agent>     Agent: claude (default), codex
#   -P <platform>  Platform: auto (default), discord, or telegram
#   --thread       Each task gets its own Discord thread
#   --tg-chat <id> Telegram chat id (when -P telegram)
#   --tg-thread <id> Telegram message_thread_id (optional)
#   --skip-reads   Hide Read events
#   --worktree     Use git worktrees instead of separate repos
#
# Each task runs in its own relay session. All post to the same Discord channel
# but in separate threads (when --thread is used). A summary message is posted
# when all tasks complete.

set -euo pipefail

TIMEOUT=1800
AGENT="claude"
THREAD_MODE=false
SKIP_READS=false
USE_WORKTREE=false
PLATFORM="${CODEFLOW_DEFAULT_PLATFORM:-${CODEFLOW_PLATFORM:-auto}}"
TG_CHAT_ID=""
TG_THREAD_ID=""
CODEFLOW_SAFE_MODE="$(printf '%s' "${CODEFLOW_SAFE_MODE:-false}" | tr '[:upper:]' '[:lower:]')"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PY_DIR="$(cd "$SCRIPT_DIR/../py" && pwd)"

source "$SCRIPT_DIR/lib.sh"
codeflow_init_default_paths "$ROOT_DIR"
CODEFLOW_SCRIPT_DIR="$PY_DIR"
codeflow_require_python310

STATE_FILE="${CODEFLOW_STATE_FILE:-$CODEFLOW_STATE_FILE_DEFAULT}"
STATE_FILE_READ="$STATE_FILE"

state_get() {
  local key="$1"
  codeflow_state_get "$STATE_FILE_READ" "$key"
}

# Parse options
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --thread)      THREAD_MODE=true; shift ;;
    --skip-reads)  SKIP_READS=true; shift ;;
    --worktree)    USE_WORKTREE=true; shift ;;
    --tg-chat)     TG_CHAT_ID="$2"; shift 2 ;;
    --tg-thread)   TG_THREAD_ID="$2"; shift 2 ;;
    -t) TIMEOUT="$2"; shift 2 ;;
    -a) AGENT="$2"; shift 2 ;;
    -P) PLATFORM="$2"; shift 2 ;;
    -*) echo "Unknown option: $1" >&2; exit 1 ;;
    *)  ARGS+=("$1"); shift ;;
  esac
done

TASKS_FILE="${ARGS[0]:-}"
[ -z "$TASKS_FILE" ] && { echo "Usage: parallel-tasks.sh [options] <tasks-file>" >&2; exit 1; }
[ ! -f "$TASKS_FILE" ] && { echo "❌ Error: Tasks file not found: $TASKS_FILE" >&2; exit 1; }

# Read tasks
declare -a TASK_DIRS
declare -a TASK_PROMPTS
declare -a TASK_NAMES

TASK_COUNT=0
while IFS= read -r line || [ -n "$line" ]; do
  if parsed="$(codeflow_parse_task_line "$line")"; then
    TASK_DIR="${parsed%%$'\t'*}"
    TASK_PROMPT="${parsed#*$'\t'}"
  else
    rc=$?
    if [ "$rc" -eq 2 ]; then
      echo "⚠️  Skipping invalid line: $line" >&2
    fi
    continue
  fi

  # Expand ~ in path
  TASK_DIR="${TASK_DIR/#\~/$HOME}"

  TASK_DIRS+=("$TASK_DIR")
  TASK_PROMPTS+=("$TASK_PROMPT")
  TASK_NAMES+=("$(basename "$TASK_DIR")")
  TASK_COUNT=$((TASK_COUNT + 1))
done < "$TASKS_FILE"

[ "$TASK_COUNT" -eq 0 ] && { echo "❌ Error: No valid tasks found in $TASKS_FILE" >&2; exit 1; }

echo "🚀 Starting $TASK_COUNT parallel Codeflow sessions"
echo "  Agent: $AGENT | Timeout: ${TIMEOUT}s | Thread: $THREAD_MODE"
echo ""

# Platform target for summary message
PLATFORM="$(codeflow_infer_platform "$ROOT_DIR" "$PLATFORM" "$STATE_FILE_READ" "$TG_CHAT_ID" "$TG_THREAD_ID")"
if [ "$PLATFORM" = "telegram" ]; then
  codeflow_resolve_openclaw_session_context
  [ -z "$TG_CHAT_ID" ] && TG_CHAT_ID="$(state_get telegram_chat_id)"
  [ -z "$TG_THREAD_ID" ] && TG_THREAD_ID="$(state_get telegram_thread_id)"
fi

WEBHOOK_URL=""
if [ "$PLATFORM" = "discord" ]; then
  if [ -f "$ROOT_DIR/.webhook-url" ]; then
    WEBHOOK_URL="$(tr -d '\n' < "$ROOT_DIR/.webhook-url")"
  fi
  [ -z "$WEBHOOK_URL" ] && {
    echo "❌ Error: .webhook-url not found in $ROOT_DIR" >&2
    echo "  Create it: echo 'https://discord.com/api/webhooks/ID/TOKEN' > $ROOT_DIR/.webhook-url" >&2
    exit 1
  }
fi

post_summary() {
  local msg="$1"
  local redacted

  redacted="$(
    printf %s "$msg" | PYTHONPATH="$PY_DIR" python3 -c '
import sys
from redaction import redact_text

strict = sys.argv[1].strip().lower() in {"1", "true", "yes", "y", "on"}
sys.stdout.write(redact_text(sys.stdin.read(), strict=strict))
' "$CODEFLOW_SAFE_MODE" 2>/dev/null || printf %s "$msg"
  )"
  msg="$redacted"

  if [ "$PLATFORM" = "telegram" ]; then
    local tg_token tg_chat tg_thread
    tg_token="${TELEGRAM_BOT_TOKEN:-}"
    tg_chat="${TG_CHAT_ID:-${CODEFLOW_TELEGRAM_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}}"
    tg_thread="${TG_THREAD_ID:-${CODEFLOW_TELEGRAM_THREAD_ID:-${TELEGRAM_THREAD_ID:-}}}"

    if [ -z "$tg_token" ]; then
      tg_token="$(python3 - <<'PY'
import json, os
from pathlib import Path
p = Path(os.environ.get('OPENCLAW_CONFIG_PATH','~/.openclaw/openclaw.json')).expanduser()
try:
    d = json.loads(p.read_text(encoding='utf-8'))
    print((((d.get('channels') or {}).get('telegram') or {}).get('botToken') or '').strip())
except Exception:
    print('')
PY
)" || true
    fi

    [ -z "$tg_token" ] && return 0
    [ -z "$tg_chat" ] && return 0
    # Note: platforms/telegram.py handles message splitting (MAX_TEXT); no pre-truncation here.

    printf %s "$msg" | CODEFLOW_POST_NAME="Codeflow Parallel" \
      PYTHONPATH="$PY_DIR" \
      TELEGRAM_BOT_TOKEN="$tg_token" \
      TELEGRAM_CHAT_ID="$tg_chat" \
      TELEGRAM_THREAD_ID="$tg_thread" \
      python3 -c '
import os
import sys
from platforms import telegram

name = (os.environ.get("CODEFLOW_POST_NAME") or "").strip() or None
telegram.post(sys.stdin.read(), name)
' 2>/dev/null || true
    return 0
  fi

  [ -z "$WEBHOOK_URL" ] && return 0
  # Note: platforms/discord.py handles message splitting (MAX_TEXT); no pre-truncation here.
  printf %s "$msg" | CODEFLOW_POST_NAME="Codeflow Parallel" \
    PYTHONPATH="$PY_DIR" \
    PLATFORM="discord" \
    THREAD_MODE="false" \
    WEBHOOK_URL="$WEBHOOK_URL" \
    AGENT_NAME="Codeflow Parallel" \
    python3 -c '
import os
import sys
from platforms import get_platform

name = (os.environ.get("CODEFLOW_POST_NAME") or "").strip() or None
get_platform("discord").post(sys.stdin.read(), name)
' 2>/dev/null || true
}

# Post start message
TASK_LIST=""
for i in $(seq 0 $((TASK_COUNT - 1))); do
  TASK_LIST="${TASK_LIST}\n  ${i+1}. \`${TASK_NAMES[$i]}\` — ${TASK_PROMPTS[$i]:0:60}"
done
post_summary "🔀 **Parallel Session Started** — $TASK_COUNT tasks$(echo -e "$TASK_LIST")"

# Launch all tasks
declare -a PIDS
declare -a RELAY_DIRS

for i in $(seq 0 $((TASK_COUNT - 1))); do
  TASK_DIR="${TASK_DIRS[$i]}"
  TASK_PROMPT="${TASK_PROMPTS[$i]}"
  TASK_NAME="${TASK_NAMES[$i]}"

  # Setup worktree if requested
  WORK_DIR="$TASK_DIR"
  if [ "$USE_WORKTREE" = true ] && [ -d "$TASK_DIR/.git" ]; then
    WT_DIR="/tmp/codeflow-wt-${TASK_NAME}-$$"
    BRANCH="codeflow-${TASK_NAME}-$$"
    if (cd "$TASK_DIR" && git worktree add "$WT_DIR" -b "$BRANCH" HEAD 2>/dev/null); then
      WORK_DIR="$WT_DIR"
      echo "  📂 Worktree: $WT_DIR (branch: $BRANCH)"
    else
      echo "  ⚠️  Worktree failed for $TASK_NAME, using original dir" >&2
    fi
  fi

  # Build agent command
  COMPLETION_MSG="When completely finished, run: openclaw system event --text 'Done: ${TASK_NAME} - task complete' --mode now"
  AGENT_ARGS=()
  case "$AGENT" in
    claude*)
      AGENT_ARGS=(claude -p --dangerously-skip-permissions --output-format stream-json --verbose "${TASK_PROMPT}. ${COMPLETION_MSG}")
      ;;
    codex*)
      AGENT_ARGS=(codex exec --json --full-auto "${TASK_PROMPT}. ${COMPLETION_MSG}")
      ;;
    *)
      read -r -a AGENT_WORDS <<< "$AGENT"
      AGENT_ARGS=("${AGENT_WORDS[@]}" "$TASK_PROMPT")
      ;;
  esac

  # Build relay flags
  RELAY_ARGS=(-w "$WORK_DIR" -t "$TIMEOUT" -P "$PLATFORM" -n "${AGENT} [$TASK_NAME]")
  # Always use threads for parallel on Discord so tasks don't interleave
  if [ "$PLATFORM" = "discord" ]; then
    RELAY_ARGS+=(--thread)
  fi
  [ "$SKIP_READS" = true ] && RELAY_ARGS+=(--skip-reads)
  [ -n "$TG_CHAT_ID" ] && RELAY_ARGS+=(--tg-chat "$TG_CHAT_ID")
  [ -n "$TG_THREAD_ID" ] && RELAY_ARGS+=(--tg-thread "$TG_THREAD_ID")

  echo "  🚀 Task $((i + 1))/$TASK_COUNT: $TASK_NAME"

  # Launch in background
  bash "$SCRIPT_DIR/dev-relay.sh" "${RELAY_ARGS[@]}" -- "${AGENT_ARGS[@]}" &
  PIDS+=($!)

  # Small stagger to avoid webhook collision on thread creation
  sleep 2
done

echo ""
echo "⏳ Waiting for $TASK_COUNT tasks to complete..."

# Wait for all and collect exit codes
declare -a EXIT_CODES
FAILED=0
SUCCEEDED=0

for i in $(seq 0 $((TASK_COUNT - 1))); do
  if wait "${PIDS[$i]}" 2>/dev/null; then
    EC=0
  else
    EC=$?
  fi
  EXIT_CODES+=($EC)
  if [ "$EC" -eq 0 ]; then
    SUCCEEDED=$((SUCCEEDED + 1))
    echo "  ✅ Task $((i + 1)) (${TASK_NAMES[$i]}): completed"
  else
    FAILED=$((FAILED + 1))
    echo "  ❌ Task $((i + 1)) (${TASK_NAMES[$i]}): failed (exit $EC)"
  fi
done

# Cleanup worktrees
if [ "$USE_WORKTREE" = true ]; then
  for i in $(seq 0 $((TASK_COUNT - 1))); do
    TASK_DIR="${TASK_DIRS[$i]}"
    TASK_NAME="${TASK_NAMES[$i]}"
    WT_DIR="/tmp/codeflow-wt-${TASK_NAME}-$$"
    BRANCH="codeflow-${TASK_NAME}-$$"
    if [ -d "$WT_DIR" ]; then
      (cd "$TASK_DIR" && git worktree remove "$WT_DIR" --force 2>/dev/null) || true
      (cd "$TASK_DIR" && git branch -D "$BRANCH" 2>/dev/null) || true
    fi
  done
fi

# Post summary
SUMMARY="🏁 **Parallel Session Complete**\n"
SUMMARY="${SUMMARY}  ✅ ${SUCCEEDED} succeeded | ❌ ${FAILED} failed | Total: ${TASK_COUNT}\n"
for i in $(seq 0 $((TASK_COUNT - 1))); do
  ICON="✅"
  [ "${EXIT_CODES[$i]}" -ne 0 ] && ICON="❌"
  SUMMARY="${SUMMARY}\n  ${ICON} \`${TASK_NAMES[$i]}\` — ${TASK_PROMPTS[$i]:0:60}"
done

post_summary "$(echo -e "$SUMMARY")"

echo ""
echo "Done. $SUCCEEDED/$TASK_COUNT tasks succeeded."
[ "$FAILED" -gt 0 ] && exit 1
exit 0
