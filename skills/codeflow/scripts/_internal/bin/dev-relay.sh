#!/bin/bash
# dev-relay.sh — Stream coding agent output to Discord #dev-session
#
# Usage: ./dev-relay.sh [options] -- <command>
#   ./dev-relay.sh -w ~/projects/foo -- claude -p --dangerously-skip-permissions --output-format stream-json --verbose 'build a REST API'
#   ./dev-relay.sh -w ~/project -- codex exec --full-auto 'fix tests'
#
# Options:
#   -w <dir>        Working directory (default: current dir)
#   -t <seconds>    Timeout (default: 1800 = 30min)
#   -h <seconds>    Hang threshold (default: 120)
#   -i <seconds>    Post interval (default: 10)
#   -n <name>       Agent display name (auto-detected from command)
#   -P <platform>   Chat platform: discord, telegram, or auto (defaults from CODEFLOW_PLATFORM/CODEFLOW_DEFAULT_PLATFORM)
#   --thread        Post into a Discord thread (first message creates the thread)
#   --tg-chat <id>  Telegram chat id (required when -P telegram unless env set)
#   --tg-thread <id> Telegram message_thread_id (optional, forum topics)
#   --skip-reads    Hide Read tool events from relay output
#   --resume <dir>  Replay a previous session from its stream.jsonl
#   --review <url>  PR review mode: clone, review, stream (see review-pr.sh)
#   --parallel <f>  Parallel tasks mode: run tasks from file across worktrees
#   --new-session   For Codex exec: force a new Codex session (ignore cached one)
#   --reuse-session For Codex exec: require and reuse previous session for this workdir
#   --activate      Activate Codeflow guard for current chat/session context
#   --deactivate    Deactivate Codeflow guard
#   --guard-status  Print current Codeflow guard state
#
# For Claude Code: uses -p --output-format stream-json --verbose for clean JSON output
# Prerequisites: ~/.claude/settings.json with defaultMode: "bypassPermissions"

set -euo pipefail
umask 077

WORKDIR="$(pwd)"
TIMEOUT=1800
HANG_THRESHOLD=120
INTERVAL=10
AGENT_NAME=""
PLATFORM="${CODEFLOW_DEFAULT_PLATFORM:-${CODEFLOW_PLATFORM:-discord}}"
THREAD_MODE=false
SKIP_READS=false
RESUME_DIR=""
REVIEW_PR=""
PARALLEL_FILE=""
TG_CHAT_ID=""
TG_THREAD_ID=""
CODEX_SESSION_POLICY="${CODEFLOW_CODEX_SESSION_MODE:-auto}"   # auto|new|reuse
CODEX_SESSION_MAP="${CODEFLOW_CODEX_SESSION_MAP:-/tmp/dev-relay-codex-sessions.json}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PY_DIR="$(cd "$SCRIPT_DIR/../py" && pwd)"
source "$SCRIPT_DIR/lib.sh"
codeflow_init_default_paths "$ROOT_DIR"
CODEFLOW_SCRIPT_DIR="$PY_DIR"
codeflow_require_python310

STATE_FILE="${CODEFLOW_STATE_FILE:-$CODEFLOW_STATE_FILE_DEFAULT}"
STATE_FILE_READ="$STATE_FILE"

GUARD_FILE="${CODEFLOW_GUARD_FILE:-$CODEFLOW_GUARD_FILE_DEFAULT}"
AUDIT_FILE="${CODEFLOW_AUDIT_FILE:-$CODEFLOW_AUDIT_FILE_DEFAULT}"
ENFORCE_GUARD="${CODEFLOW_ENFORCE_GUARD:-true}"
GUARD_ACTIVATE=false
GUARD_DEACTIVATE=false
GUARD_STATUS=false

# Telegram UI feedback (set CODEFLOW_TG_TYPING_ENABLED=false to disable)
CODEFLOW_TG_TYPING_ENABLED="${CODEFLOW_TG_TYPING_ENABLED:-true}"
CODEFLOW_TG_TYPING_INTERVAL="${CODEFLOW_TG_TYPING_INTERVAL:-4}"

# Safety mode: suppress high-risk content in relay output (default OFF).
# Enabled when CODEFLOW_SAFE_MODE=true.
CODEFLOW_SAFE_MODE="$(printf '%s' "${CODEFLOW_SAFE_MODE:-false}" | tr '[:upper:]' '[:lower:]')"

# Parse long options first, converting them to positional args for getopts
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --thread)     THREAD_MODE=true; shift ;;
    --skip-reads) SKIP_READS=true; shift ;;
    --resume)     RESUME_DIR="$2"; shift 2 ;;
    --review)     REVIEW_PR="$2"; shift 2 ;;
    --parallel)   PARALLEL_FILE="$2"; shift 2 ;;
    --tg-chat)    TG_CHAT_ID="$2"; shift 2 ;;
    --tg-thread)  TG_THREAD_ID="$2"; shift 2 ;;
    --new-session)   CODEX_SESSION_POLICY="new"; shift ;;
    --reuse-session) CODEX_SESSION_POLICY="reuse"; shift ;;
    --activate)   GUARD_ACTIVATE=true; shift ;;
    --deactivate) GUARD_DEACTIVATE=true; shift ;;
    --guard-status) GUARD_STATUS=true; shift ;;
    --)           ARGS+=("--"); shift; ARGS+=("$@"); break ;;
    *)            ARGS+=("$1"); shift ;;
  esac
done
if [ ${#ARGS[@]} -gt 0 ]; then set -- "${ARGS[@]}"; else set --; fi

while getopts "w:t:h:i:n:P:" opt; do
  case $opt in
    w) WORKDIR="$OPTARG" ;;
    t) TIMEOUT="$OPTARG" ;;
    h) HANG_THRESHOLD="$OPTARG" ;;
    i) INTERVAL="$OPTARG" ;;
    n) AGENT_NAME="$OPTARG" ;;
    P) PLATFORM="$OPTARG" ;;
    *) exit 1 ;;
  esac
done
shift $((OPTIND - 1))
[ "${1:-}" = "--" ] && shift

COMMAND_ARGS=("$@")
COMMAND="$*"
WORKDIR_ABS=$(python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$WORKDIR" 2>/dev/null || echo "$WORKDIR")

get_codex_session_for_workdir() {
  python3 - "$CODEX_SESSION_MAP" "$WORKDIR_ABS" <<'PY'
import json, sys
path, key = sys.argv[1], sys.argv[2]
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        v = data.get(key, '')
        if isinstance(v, str):
            print(v.strip())
except Exception:
    pass
PY
}

set_codex_session_for_workdir() {
  local sid="$1"
  [ -z "$sid" ] && return 0
  python3 - "$CODEX_SESSION_MAP" "$WORKDIR_ABS" "$sid" <<'PY'
import fcntl
import json
import os
import sys
import tempfile
path, key, sid = sys.argv[1], sys.argv[2], sys.argv[3]
obj = {}

dir_path = os.path.dirname(path) or "."
os.makedirs(dir_path, exist_ok=True)
lock_path = path + ".lock"
lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    try:
        with open(path, "r", encoding="utf-8") as f:
            cur = json.load(f)
            if isinstance(cur, dict):
                obj = cur
    except Exception:
        obj = {}

    obj[key] = sid

    fd, tmp = tempfile.mkstemp(prefix="codeflow-sessions-", dir=dir_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        os.replace(tmp, path)
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass

        try:
            dfd = os.open(dir_path, os.O_DIRECTORY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except Exception:
            pass
    finally:
        try:
            if os.path.exists(tmp):
                os.unlink(tmp)
        except Exception:
            pass
finally:
    try:
        os.close(lock_fd)
    except Exception:
        pass
PY
}

state_get() {
  local key="$1"
  codeflow_state_get "$STATE_FILE_READ" "$key"
}

state_set() {
  local key="$1"
  local value="$2"
  codeflow_state_set "$STATE_FILE" "$key" "$value"
}

guard_enabled() {
  local v
  v="$(printf '%s' "$ENFORCE_GUARD" | tr '[:upper:]' '[:lower:]')"
  case "$v" in
    false|0|no|off) return 1 ;;
    *) return 0 ;;
  esac
}

run_guard() {
  local action="$1"
  shift || true
  local session_key
  session_key="${OPENCLAW_SESSION_KEY:-${OPENCLAW_SESSION:-}}"
  python3 "$PY_DIR/codeflow-guard.py" "$action" \
    --state "$GUARD_FILE" \
    --audit "$AUDIT_FILE" \
    --session-key "$session_key" \
    --platform "${PLATFORM:-}" \
    --chat-id "${TELEGRAM_CHAT_ID:-${TG_CHAT_ID:-}}" \
    --thread-id "${TELEGRAM_THREAD_ID:-${TG_THREAD_ID:-}}" \
    --workdir "$WORKDIR_ABS" \
    --agent "${AGENT_NAME:-}" \
    --command "$COMMAND" \
    "$@"
}

resolve_openclaw_session_context() {
  codeflow_resolve_openclaw_session_context
}

setup_platform_env() {
  PLATFORM="$(codeflow_infer_platform "$ROOT_DIR" "$PLATFORM" "$STATE_FILE_READ" "$TG_CHAT_ID" "$TG_THREAD_ID")"

  case "$PLATFORM" in
    discord)
      WEBHOOK_URL=""
      if [ -f "$ROOT_DIR/.webhook-url" ]; then
        WEBHOOK_URL="$(tr -d '\n' < "$ROOT_DIR/.webhook-url")"
      fi
      [ -z "$WEBHOOK_URL" ] && {
        echo "❌ Error: .webhook-url not found in $ROOT_DIR" >&2
        echo "  Create it: echo 'https://discord.com/api/webhooks/ID/TOKEN' > $ROOT_DIR/.webhook-url" >&2
        exit 1
      }

      if ! WEBHOOK_URL="$WEBHOOK_URL" python3 - <<'PY'
import os
import sys
import urllib.request

url = (os.environ.get("WEBHOOK_URL") or "").strip()
if not url:
    sys.exit(1)

try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        code = getattr(resp, "status", None) or resp.getcode()
    sys.exit(0 if int(code) == 200 else 1)
except Exception:
    sys.exit(1)
PY
      then
        echo "❌ Error: Webhook URL appears invalid or unreachable" >&2
        echo "  Check: $ROOT_DIR/.webhook-url" >&2
        exit 1
      fi

      BOT_TOKEN="${CODEFLOW_BOT_TOKEN:-}"
      if [ -z "$BOT_TOKEN" ] && command -v security &>/dev/null; then
        BOT_TOKEN=$(security find-generic-password -s discord-bot-token -a codeflow -w 2>/dev/null || true)
      fi
      if [ -z "$BOT_TOKEN" ] && [ -f "$ROOT_DIR/.bot-token" ]; then
        BOT_TOKEN="$(tr -d '\n' < "$ROOT_DIR/.bot-token")"
      fi
      if [ "$THREAD_MODE" = true ] && [ -z "$BOT_TOKEN" ]; then
        echo "⚠️  Warning: --thread requires a bot token for text channels" >&2
        echo "  Create: echo 'YOUR_BOT_TOKEN' > $ROOT_DIR/.bot-token" >&2
        echo "  Falling back to non-thread mode" >&2
        THREAD_MODE=false
      fi
      ;;

    telegram)
      WEBHOOK_URL=""
      BOT_TOKEN=""
      [ "$THREAD_MODE" = true ] && {
        echo "⚠️  Warning: --thread is Discord-only; ignored for Telegram." >&2
        THREAD_MODE=false
      }

      TELEGRAM_CHAT_ID="${TG_CHAT_ID:-${CODEFLOW_TELEGRAM_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}}"
      TELEGRAM_THREAD_ID="${TG_THREAD_ID:-${CODEFLOW_TELEGRAM_THREAD_ID:-${TELEGRAM_THREAD_ID:-}}}"
      TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"

      resolve_openclaw_session_context
      [ -z "$TELEGRAM_CHAT_ID" ] && TELEGRAM_CHAT_ID="$(state_get telegram_chat_id)"
      [ -z "$TELEGRAM_THREAD_ID" ] && TELEGRAM_THREAD_ID="$(state_get telegram_thread_id)"

      if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        TELEGRAM_BOT_TOKEN=$(python3 - <<'PY'
import json, os
from pathlib import Path
p = Path(os.environ.get('OPENCLAW_CONFIG_PATH','~/.openclaw/openclaw.json')).expanduser()
try:
    d = json.loads(p.read_text(encoding='utf-8'))
    print((((d.get('channels') or {}).get('telegram') or {}).get('botToken') or '').strip())
except Exception:
    print('')
PY
)
      fi

      [ -z "$TELEGRAM_BOT_TOKEN" ] && { echo "❌ Error: Telegram bot token missing. Set TELEGRAM_BOT_TOKEN or configure channels.telegram.botToken" >&2; exit 1; }
      [ -z "$TELEGRAM_CHAT_ID" ] && { echo "❌ Error: Telegram chat id missing. Use --tg-chat <chat_id> (or CODEFLOW_TELEGRAM_CHAT_ID)." >&2; exit 1; }

      state_set telegram_chat_id "$TELEGRAM_CHAT_ID"
      state_set telegram_thread_id "$TELEGRAM_THREAD_ID"

      if ! TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" python3 - <<'PY'
import json
import os
import sys
import urllib.request

tok = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
if not tok:
    sys.exit(1)

url = f"https://api.telegram.org/bot{tok}/getMe"
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    data = json.loads(raw)
    ok = isinstance(data, dict) and data.get("ok") is True
    sys.exit(0 if ok else 1)
except Exception:
    sys.exit(1)
PY
      then
        echo "❌ Error: Telegram bot token appears invalid/unreachable" >&2
        exit 1
      fi
      ;;

    *)
      echo "❌ Error: Unsupported platform '$PLATFORM'. Supported: discord, telegram" >&2
      exit 1
      ;;
  esac
}

setup_platform_env

# Guard management actions
if [ "$GUARD_ACTIVATE" = true ]; then
  run_guard activate
  echo "Codeflow guard activated."
  exit 0
fi

if [ "$GUARD_DEACTIVATE" = true ]; then
  run_guard deactivate
  echo "Codeflow guard deactivated."
  exit 0
fi

if [ "$GUARD_STATUS" = true ]; then
  run_guard status
  exit 0
fi

# Guard precheck: block runs unless Codeflow guard is active for this context
if guard_enabled; then
  if ! run_guard check; then
    echo "❌ Error: Codeflow guard blocked this run. Send /codeflow in this chat/topic, then retry." >&2
    exit 42
  fi
fi

# Resume mode: replay from existing stream.jsonl
if [ -n "$RESUME_DIR" ]; then
  STREAM_FILE="$RESUME_DIR/stream.jsonl"
  [ ! -f "$STREAM_FILE" ] && { echo "❌ Error: $STREAM_FILE not found" >&2; exit 1; }

  export WEBHOOK_URL AGENT_NAME PLATFORM THREAD_MODE SKIP_READS BOT_TOKEN
  export TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID TELEGRAM_THREAD_ID
  export RELAY_DIR="$RESUME_DIR"
  export REPLAY_MODE=true

  echo "🔄 Replaying session from $STREAM_FILE"
  PARSER="$PY_DIR/parse-stream.py"
  python3 "$PARSER" < "$STREAM_FILE"
  echo "Done."
  exit 0
fi

# Review mode: delegate to review-pr.sh
if [ -n "$REVIEW_PR" ]; then
  REVIEW_FLAGS=(-P "$PLATFORM" -t "$TIMEOUT")
  [ "$THREAD_MODE" = true ] && REVIEW_FLAGS+=(--thread)
  [ "$SKIP_READS" = true ] && REVIEW_FLAGS+=(--skip-reads)
  [ -n "$WORKDIR" ] && [ "$WORKDIR" != "$(pwd)" ] && REVIEW_FLAGS+=(-w "$WORKDIR")
  [ -n "$TG_CHAT_ID" ] && REVIEW_FLAGS+=(--tg-chat "$TG_CHAT_ID")
  [ -n "$TG_THREAD_ID" ] && REVIEW_FLAGS+=(--tg-thread "$TG_THREAD_ID")
  # Pass remaining args as review options (e.g., -a codex, -p "custom prompt", -c)
  exec bash "$SCRIPT_DIR/review-pr.sh" "${REVIEW_FLAGS[@]}" "${COMMAND_ARGS[@]}" "$REVIEW_PR"
fi

# Parallel mode: delegate to parallel-tasks.sh
if [ -n "$PARALLEL_FILE" ]; then
  PARA_FLAGS=(-P "$PLATFORM" -t "$TIMEOUT")
  [ "$THREAD_MODE" = true ] && PARA_FLAGS+=(--thread)
  [ "$SKIP_READS" = true ] && PARA_FLAGS+=(--skip-reads)
  [ -n "$TG_CHAT_ID" ] && PARA_FLAGS+=(--tg-chat "$TG_CHAT_ID")
  [ -n "$TG_THREAD_ID" ] && PARA_FLAGS+=(--tg-thread "$TG_THREAD_ID")
  exec bash "$SCRIPT_DIR/parallel-tasks.sh" "${PARA_FLAGS[@]}" "$PARALLEL_FILE"
fi

[ -z "$COMMAND" ] && { echo "Usage: dev-relay.sh [options] -- <command>" >&2; exit 1; }

# Auto-detect agent name and mode
IS_CLAUDE=false
IS_CODEX=false
if [ -z "$AGENT_NAME" ]; then
  case "$COMMAND" in
    claude*) AGENT_NAME="Claude Code"; IS_CLAUDE=true ;;
    codex*)  AGENT_NAME="Codex"; IS_CODEX=true ;;
    gemini*) AGENT_NAME="Gemini CLI" ;;
    pi*)     AGENT_NAME="Pi Agent" ;;
    *)       AGENT_NAME="Agent" ;;
  esac
fi
# Codex session reuse policy (forced by code path for codex exec)
if [ "$IS_CODEX" = true ] && [ "${COMMAND_ARGS[0]:-}" = "codex" ] && [ "${COMMAND_ARGS[1]:-}" = "exec" ]; then
  IS_CODEX_EXEC=true
  IS_CODEX_EXEC_RESUME=false
  [ "${COMMAND_ARGS[2]:-}" = "resume" ] && IS_CODEX_EXEC_RESUME=true

  if [ "$IS_CODEX_EXEC_RESUME" = false ]; then
    EXPLICIT_NEW=false
    if printf '%s\n' "${COMMAND_ARGS[@]:2}" | grep -Eq '(^|[[:space:]])/new([[:space:]]|$)'; then
      EXPLICIT_NEW=true
    fi

    EFFECTIVE_POLICY="$CODEX_SESSION_POLICY"
    if [ "$EXPLICIT_NEW" = true ] && [ "$CODEX_SESSION_POLICY" = "auto" ]; then
      EFFECTIVE_POLICY="new"
    fi

    LAST_CODEX_SESSION="$(get_codex_session_for_workdir)"
    case "$EFFECTIVE_POLICY" in
      reuse)
        if [ -z "$LAST_CODEX_SESSION" ]; then
          echo "❌ Error: --reuse-session set, but no previous Codex session found for $WORKDIR_ABS" >&2
          exit 1
        fi
        COMMAND_ARGS=(codex exec resume "$LAST_CODEX_SESSION" "${COMMAND_ARGS[@]:2}")
        ;;
      auto)
        if [ -n "$LAST_CODEX_SESSION" ]; then
          COMMAND_ARGS=(codex exec resume "$LAST_CODEX_SESSION" "${COMMAND_ARGS[@]:2}")
        fi
        ;;
      new)
        ;;
      *)
        echo "❌ Error: invalid CODEX session policy '$CODEX_SESSION_POLICY' (expected auto|new|reuse)" >&2
        exit 1
        ;;
    esac

    COMMAND=$(printf '%q ' "${COMMAND_ARGS[@]}")
    COMMAND="${COMMAND% }"
  fi
fi

# Detect if Codex command includes --json for structured parsing
if [ "$IS_CODEX" = true ]; then
  case "$COMMAND" in
    *--json*|*--experimental-json*) IS_CODEX_JSON=true ;;
    *) IS_CODEX_JSON=false ;;
  esac
else
  IS_CODEX_JSON=false
fi

# Check unbuffer for Claude Code
if [ "$IS_CLAUDE" = true ] && ! command -v unbuffer &>/dev/null; then
  echo "❌ Error: 'unbuffer' not found (required for Claude Code streaming)" >&2
  echo "  Install: brew install expect (macOS) or apt install expect (Linux)" >&2
  exit 1
fi

# Cleanup stale relay dirs (>7 days) owned by current user (portable; best-effort)
python3 - <<'PY' 2>/dev/null || true
import os
import shutil
import stat
import sys
import time

ROOT = "/tmp"
PREFIX = "dev-relay."
cutoff = time.time() - (7 * 24 * 60 * 60)
uid = os.getuid() if hasattr(os, "getuid") else None

try:
    names = os.listdir(ROOT)
except Exception:
    sys.exit(0)

for name in names:
    if not name.startswith(PREFIX):
        continue
    path = os.path.join(ROOT, name)
    try:
        st = os.lstat(path)
    except Exception:
        continue

    if not stat.S_ISDIR(st.st_mode):
        continue
    if uid is not None and getattr(st, "st_uid", uid) != uid:
        continue
    if getattr(st, "st_mtime", cutoff + 1) > cutoff:
        continue

    try:
        shutil.rmtree(path)
    except Exception:
        pass
PY

# Temp workspace
RELAY_DIR=$(mktemp -d /tmp/dev-relay.XXXXXX)
STRUCTURED_RELAY=false
EXIT_CODE=0
TIMED_OUT=false
# Ensure stream.jsonl exists for the relay dir (parse-stream appends when structured).
: > "$RELAY_DIR/stream.jsonl" 2>/dev/null || true

echo "📂 Relay: $RELAY_DIR"
echo "🚀 $AGENT_NAME | 📁 $WORKDIR | 🎯 $PLATFORM"

telegram_send_action() {
  local action="${1:-typing}"
  local enabled

  enabled="$(printf '%s' "${CODEFLOW_TG_TYPING_ENABLED:-true}" | tr '[:upper:]' '[:lower:]')"
  [ "$enabled" = "false" ] && return 0
  [ "$enabled" = "0" ] && return 0
  [ "$enabled" = "off" ] && return 0
  [ "$PLATFORM" != "telegram" ] && return 0
  [ -z "${TELEGRAM_BOT_TOKEN:-}" ] && return 0
  [ -z "${TELEGRAM_CHAT_ID:-}" ] && return 0

  ACTION="$action" \
    PYTHONPATH="$PY_DIR" \
    TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
    TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID" \
    TELEGRAM_THREAD_ID="${TELEGRAM_THREAD_ID:-}" \
    python3 - <<'PY' 2>/dev/null || true
import os
from platforms import telegram

telegram.send_action(os.environ.get("ACTION", "typing"))
PY
}

# --- Platform posting (used for start/timeout/completion messages from bash) ---
post() {
  local msg="$1" name="${2:-$AGENT_NAME}"
  local redacted

  # Minimal redaction always; stricter when CODEFLOW_SAFE_MODE=true.
  # Keep this logic self-contained (bash sends messages too, not only parse-stream.py).
  redacted=$(
    printf %s "$msg" | PYTHONPATH="$PY_DIR" python3 -c '
import sys
from redaction import redact_text

strict = sys.argv[1].strip().lower() in {"1", "true", "yes", "y", "on"}
sys.stdout.write(redact_text(sys.stdin.read(), strict=strict))
' "$CODEFLOW_SAFE_MODE" 2>/dev/null || printf %s "$msg"
  )
  msg="$redacted"

	  if [ "$PLATFORM" = "telegram" ]; then
	    [ -z "${TELEGRAM_BOT_TOKEN:-}" ] && return
	    [ -z "${TELEGRAM_CHAT_ID:-}" ] && return
	    # Note: platforms/telegram.py handles message splitting (MAX_TEXT); no pre-truncation here.
	    printf %s "$msg" | CODEFLOW_POST_NAME="$name" \
	      PYTHONPATH="$PY_DIR" \
	      TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
	      TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID" \
	      TELEGRAM_THREAD_ID="${TELEGRAM_THREAD_ID:-}" \
      python3 -c '
import os
import sys
from platforms import telegram

name = (os.environ.get("CODEFLOW_POST_NAME") or "").strip() or None
telegram.post(sys.stdin.read(), name)
' 2>/dev/null || true
    return
  fi
	
	  # Discord default
	  [ -z "${WEBHOOK_URL:-}" ] && return
	  # Note: platforms/discord.py handles message splitting (MAX_TEXT); no pre-truncation here.
	  printf %s "$msg" | CODEFLOW_POST_NAME="$name" \
	    PYTHONPATH="$PY_DIR" \
	    PLATFORM="discord" \
	    THREAD_MODE="false" \
	    WEBHOOK_URL="$WEBHOOK_URL" \
    AGENT_NAME="$AGENT_NAME" \
    BOT_TOKEN="$BOT_TOKEN" \
    python3 -c '
import os
import sys
from platforms import get_platform

name = (os.environ.get("CODEFLOW_POST_NAME") or "").strip() or None
get_platform("discord").post(sys.stdin.read(), name)
' 2>/dev/null || true
}

PARSER="$PY_DIR/parse-stream.py"

# --- Start ---
telegram_send_action "typing"
post "🚀 **${AGENT_NAME} Session Started**
\`\`\`
${COMMAND}
\`\`\`
📁 \`${WORKDIR}\` | ⏱️ ${TIMEOUT}s timeout"

telegram_send_action "typing"
cd "$WORKDIR"

# Write command to temp script to preserve quoting
CMD_FILE="$RELAY_DIR/cmd.sh"
printf '#!/bin/bash\ncd %q\n' "$WORKDIR" > "$CMD_FILE"
printf 'echo $$ > %q\n' "$RELAY_DIR/agent.pid" >> "$CMD_FILE"
printf 'exec ' >> "$CMD_FILE"
printf '%q ' "${COMMAND_ARGS[@]}" >> "$CMD_FILE"
printf '\n' >> "$CMD_FILE"
chmod +x "$CMD_FILE"

# Save session info (per-PID for concurrent session support)
SESSION_DIR="/tmp/dev-relay-sessions"
mkdir -p "$SESSION_DIR"
chmod 700 "$SESSION_DIR"
SESSION_FILE="$SESSION_DIR/$$.json"
SESSION_PID="$$" \
  SESSION_FILE="$SESSION_FILE" \
  SESSION_AGENT="$AGENT_NAME" \
  SESSION_WORKDIR="$WORKDIR" \
  SESSION_RELAY_DIR="$RELAY_DIR" \
  SESSION_PLATFORM="$PLATFORM" \
  SESSION_COMMAND="${COMMAND_ARGS[0]:-}" \
  SESSION_START_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  python3 - <<'PY' 2>/dev/null || true
import json
import os
import tempfile

path = os.environ.get("SESSION_FILE", "")
if not path:
    raise SystemExit(0)

data = {
    "pid": int(os.environ.get("SESSION_PID", "0") or "0"),
    "agent": os.environ.get("SESSION_AGENT", ""),
    "workdir": os.environ.get("SESSION_WORKDIR", ""),
    "relayDir": os.environ.get("SESSION_RELAY_DIR", ""),
    "platform": os.environ.get("SESSION_PLATFORM", ""),
    "startTime": os.environ.get("SESSION_START_TIME", ""),
    # Minimised command surface: only keep argv[0] (binary) for debugging.
    "command": os.environ.get("SESSION_COMMAND", ""),
}

dir_path = os.path.dirname(path) or "."
fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", dir=dir_path)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass

    # Best-effort: fsync the directory to persist the rename.
    try:
        dfd = os.open(dir_path, os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except Exception:
        pass
finally:
    try:
        if os.path.exists(tmp):
            os.unlink(tmp)
    except Exception:
        pass
PY

if [ "$IS_CLAUDE" = true ] || [ "$IS_CODEX_JSON" = true ]; then
  # Structured output: pipe through parse-stream.py
  # Claude Code: stream-json via unbuffer PTY
  # Codex: --json JSONL events (no unbuffer needed)
  STRUCTURED_RELAY=true
  export WEBHOOK_URL AGENT_NAME PLATFORM THREAD_MODE SKIP_READS BOT_TOKEN
  export TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID TELEGRAM_THREAD_ID
  export RELAY_DIR
  cd "$WORKDIR"
  set -m
  if [ "$IS_CLAUDE" = true ]; then
    (unbuffer bash "$CMD_FILE" | python3 "$PARSER") &
  else
    (bash "$CMD_FILE" | python3 "$PARSER") &
  fi
  RELAY_PID=$!
  set +m
  RELAY_PGID=$(ps -o pgid= "$RELAY_PID" 2>/dev/null | tr -d ' ')
  [ -z "$RELAY_PGID" ] && RELAY_PGID=$RELAY_PID

  cleanup_relay() {
    if [ -n "${RELAY_PID:-}" ] && kill -0 "$RELAY_PID" 2>/dev/null; then
      kill -TERM -"$RELAY_PGID" 2>/dev/null
      sleep 1
      kill -KILL -"$RELAY_PGID" 2>/dev/null || true
    fi
  }
  trap cleanup_relay EXIT

  # Wait with timeout
  START=$(date +%s)
	  while kill -0 "$RELAY_PID" 2>/dev/null; do
	    NOW=$(date +%s)
	    if [ $((NOW - START)) -ge "$TIMEOUT" ]; then
	      post "⏰ **Timed out** after ${TIMEOUT}s"
	      TIMED_OUT=true
	      EXIT_CODE=124
	      cleanup_relay
	      break
	    fi
	    telegram_send_action "typing"
	    sleep "${CODEFLOW_TG_TYPING_INTERVAL}"
	  done
	  WAIT_EC=0
	  if wait "$RELAY_PID" 2>/dev/null; then
	    WAIT_EC=0
	  else
	    WAIT_EC=$?
	  fi
	  [ "$TIMED_OUT" = true ] || EXIT_CODE="$WAIT_EC"
	else
  # Non-Claude agents: raw output relay with ANSI stripping (no output.log).
  # Use `script` to force a PTY, but stream output via coprocess stdout.
  AGENT_PID=""
  RAW_SUPPRESS_NOTICE=false
  RAW_BUF=""
  coproc RAWPROC { script -q -c "bash '$CMD_FILE'" /dev/null; }
  SCRIPT_PID=$RAWPROC_PID

  cleanup() {
    if [ -n "${AGENT_PID:-}" ] && kill -0 "$AGENT_PID" 2>/dev/null; then
      kill -TERM "$AGENT_PID" 2>/dev/null
      sleep 1
      kill -KILL "$AGENT_PID" 2>/dev/null || true
    fi
    if [ -n "${SCRIPT_PID:-}" ] && kill -0 "$SCRIPT_PID" 2>/dev/null; then
      kill -TERM "$SCRIPT_PID" 2>/dev/null
      sleep 1
      kill -KILL "$SCRIPT_PID" 2>/dev/null || true
    fi
  }
  trap cleanup EXIT

  START=$(date +%s)
  LAST_OUT_TIME=$START
  HANG_WARNED=false
  LAST_TYPING_TIME=0

  flush_raw_buf() {
    local raw="$1"
    local clean=""
    [ -z "$raw" ] && return 0
    clean=$(
      printf %s "$raw" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g; s/\x1b\][^\x07]*\x07//g; s/\r//g' \
        | tr -d '\000' | head -c 1800
    )
    [ -z "$clean" ] && return 0

    if [ "$CODEFLOW_SAFE_MODE" = "true" ]; then
      if [ "$RAW_SUPPRESS_NOTICE" = false ]; then
        post "🔒 CODEFLOW_SAFE_MODE enabled — raw output suppressed (raw relay mode)"
        RAW_SUPPRESS_NOTICE=true
      fi
      return 0
    fi

    post "\`\`\`
${clean}
\`\`\`"
  }

  while true; do
    if [ -z "$AGENT_PID" ] && [ -f "$RELAY_DIR/agent.pid" ]; then
      AGENT_PID=$(tr -d '[:space:]' < "$RELAY_DIR/agent.pid" 2>/dev/null || true)
    fi

	    NOW=$(date +%s)
	    ELAPSED=$((NOW - START))
	    [ "$ELAPSED" -ge "$TIMEOUT" ] && {
	      post "⏰ **Timed out** after ${TIMEOUT}s"
	      TIMED_OUT=true
	      EXIT_CODE=124
	      cleanup
	      break
	    }
	    if [ $((NOW - LAST_TYPING_TIME)) -ge "$CODEFLOW_TG_TYPING_INTERVAL" ]; then
	      telegram_send_action "typing"
	      LAST_TYPING_TIME=$NOW
	    fi

    if IFS= read -r -t 1 LINE <&"${RAWPROC[0]}"; then
      LAST_OUT_TIME=$NOW; HANG_WARNED=false
      RAW_BUF="${RAW_BUF}${LINE}"$'\n'
      # Flush in chunks to avoid chat hard limits.
      if [ "${#RAW_BUF}" -ge 2500 ]; then
        flush_raw_buf "$RAW_BUF"
        RAW_BUF=""
      fi
    fi

    ALIVE=true
    if [ -n "$AGENT_PID" ]; then
      kill -0 "$AGENT_PID" 2>/dev/null || ALIVE=false
    else
      kill -0 "$SCRIPT_PID" 2>/dev/null || ALIVE=false
    fi

    if [ "$ALIVE" = false ]; then
      # Drain any remaining output and flush.
      while IFS= read -r -t 0.05 LINE <&"${RAWPROC[0]}"; do
        RAW_BUF="${RAW_BUF}${LINE}"$'\n'
      done
      flush_raw_buf "$RAW_BUF"
      RAW_BUF=""

	    if wait "$SCRIPT_PID" 2>/dev/null; then
	      EC=0
	    else
	      EC=$?
	    fi
	    EXIT_CODE="$EC"
	    M=$((ELAPSED / 60)); S=$((ELAPSED % 60))
	    [ "$EC" -eq 0 ] && post "✅ **Completed** (exit: ${EC}, ${M}m${S}s)" || post "❌ **Ended** (exit: ${EC}, ${M}m${S}s)"
	    break
	    fi

    SILENT=$((NOW - LAST_OUT_TIME))
    if [ "$SILENT" -ge "$HANG_THRESHOLD" ] && [ "$HANG_WARNED" = false ]; then
      post "⚠️ **No output for ${SILENT}s** — may be stuck"; HANG_WARNED=true
    fi
  done
fi

# Update Codex session mapping from current relay stream (for future reuse)
if [ "$IS_CODEX" = true ] && [ -f "$RELAY_DIR/stream.jsonl" ]; then
  CODEX_THREAD_ID=$(python3 - "$RELAY_DIR/stream.jsonl" <<'PY'
import json, sys
sid = ""
try:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get('type') == 'thread.started':
                t = d.get('thread_id', '')
                if isinstance(t, str) and t.strip():
                    sid = t.strip()
except Exception:
    pass
print(sid)
PY
)
  [ -n "$CODEX_THREAD_ID" ] && set_codex_session_for_workdir "$CODEX_THREAD_ID"
fi

END_TS=$(date +%s)
DURATION=$((END_TS - START))
if [ "$TIMED_OUT" = true ]; then
  END_MSG="⏰ **Codeflow session timed out** — ${AGENT_NAME} in ${WORKDIR} (${DURATION}s, exit: ${EXIT_CODE})"
elif [ "$EXIT_CODE" -eq 0 ]; then
  END_MSG="✅ **Codeflow session completed** — ${AGENT_NAME} finished in ${WORKDIR} (${DURATION}s, exit: ${EXIT_CODE})"
else
  END_MSG="❌ **Codeflow session ended** — ${AGENT_NAME} in ${WORKDIR} (${DURATION}s, exit: ${EXIT_CODE})"
fi
post "$END_MSG"

# Also notify OpenClaw main session (fires on next heartbeat)
if [ "$TIMED_OUT" = true ]; then
  openclaw system event --text "Codeflow timed out (exit: ${EXIT_CODE}): ${AGENT_NAME} in ${WORKDIR}" 2>/dev/null || true
elif [ "$EXIT_CODE" -eq 0 ]; then
  openclaw system event --text "Codeflow done (exit: ${EXIT_CODE}): ${AGENT_NAME} in ${WORKDIR}" 2>/dev/null || true
else
  openclaw system event --text "Codeflow ended (exit: ${EXIT_CODE}): ${AGENT_NAME} in ${WORKDIR}" 2>/dev/null || true
fi
rm -f "$SESSION_FILE" 2>/dev/null
echo "Done."
