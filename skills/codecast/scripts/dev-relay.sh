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
#   -P <platform>   Chat platform: discord (default). Others error until implemented.
#   -r <n>          Rate limit (posts per 60s, default: 25)
#   --thread        Post into a Discord thread (first message creates the thread)
#   --skip-reads    Hide Read tool events from relay output
#   --resume <dir>  Replay a previous session from its stream.jsonl
#   --review <url>  PR review mode: clone, review, stream (see review-pr.sh)
#   --parallel <f>  Parallel tasks mode: run tasks from file across worktrees
#
# For Claude Code: uses -p --output-format stream-json --verbose for clean JSON output
# Prerequisites: ~/.claude/settings.json with defaultMode: "bypassPermissions"

set -uo pipefail

WORKDIR="$(pwd)"
TIMEOUT=1800
HANG_THRESHOLD=120
INTERVAL=10
AGENT_NAME=""
PLATFORM="discord"
THREAD_MODE=false
SKIP_READS=false
RESUME_DIR=""
RATE_LIMIT=""
REVIEW_PR=""
PARALLEL_FILE=""

# Parse long options first, converting them to positional args for getopts
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --thread)     THREAD_MODE=true; shift ;;
    --skip-reads) SKIP_READS=true; shift ;;
    --resume)     RESUME_DIR="$2"; shift 2 ;;
    --review)     REVIEW_PR="$2"; shift 2 ;;
    --parallel)   PARALLEL_FILE="$2"; shift 2 ;;
    --)           ARGS+=("--"); shift; ARGS+=("$@"); break ;;
    *)            ARGS+=("$1"); shift ;;
  esac
done
if [ ${#ARGS[@]} -gt 0 ]; then set -- "${ARGS[@]}"; else set --; fi

while getopts "w:t:h:i:n:P:r:" opt; do
  case $opt in
    w) WORKDIR="$OPTARG" ;;
    t) TIMEOUT="$OPTARG" ;;
    h) HANG_THRESHOLD="$OPTARG" ;;
    i) INTERVAL="$OPTARG" ;;
    n) AGENT_NAME="$OPTARG" ;;
    P) PLATFORM="$OPTARG" ;;
    r) RATE_LIMIT="$OPTARG" ;;
    *) exit 1 ;;
  esac
done
shift $((OPTIND - 1))
[ "${1:-}" = "--" ] && shift

COMMAND_ARGS=("$@")
COMMAND="$*"

# Resume mode: replay from existing stream.jsonl
if [ -n "$RESUME_DIR" ]; then
  STREAM_FILE="$RESUME_DIR/stream.jsonl"
  [ ! -f "$STREAM_FILE" ] && { echo "❌ Error: $STREAM_FILE not found" >&2; exit 1; }

  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  WEBHOOK_URL=$(cat "$SCRIPT_DIR/.webhook-url" 2>/dev/null | tr -d '\n')
  [ -z "$WEBHOOK_URL" ] && { echo "❌ Error: .webhook-url not found" >&2; exit 1; }

  export WEBHOOK_URL AGENT_NAME PLATFORM THREAD_MODE SKIP_READS BOT_TOKEN
  export RELAY_DIR="$RESUME_DIR"
  export REPLAY_MODE=true
  [ -n "$RATE_LIMIT" ] && export CODECAST_RATE_LIMIT="$RATE_LIMIT"

  echo "🔄 Replaying session from $STREAM_FILE"
  PARSER="$SCRIPT_DIR/parse-stream.py"
  python3 "$PARSER" < "$STREAM_FILE"
  echo "Done."
  exit 0
fi

# Review mode: delegate to review-pr.sh
if [ -n "$REVIEW_PR" ]; then
  REVIEW_FLAGS=""
  [ "$THREAD_MODE" = true ] && REVIEW_FLAGS="$REVIEW_FLAGS --thread"
  [ "$SKIP_READS" = true ] && REVIEW_FLAGS="$REVIEW_FLAGS --skip-reads"
  [ -n "$RATE_LIMIT" ] && REVIEW_FLAGS="$REVIEW_FLAGS -r $RATE_LIMIT"
  [ -n "$WORKDIR" ] && [ "$WORKDIR" != "$(pwd)" ] && REVIEW_FLAGS="$REVIEW_FLAGS -w $WORKDIR"
  REVIEW_FLAGS="$REVIEW_FLAGS -t $TIMEOUT"
  # Pass remaining args as review options (e.g., -a codex, -p "custom prompt", -c)
  exec bash "$SCRIPT_DIR/review-pr.sh" $REVIEW_FLAGS "${COMMAND_ARGS[@]}" "$REVIEW_PR"
fi

# Parallel mode: delegate to parallel-tasks.sh
if [ -n "$PARALLEL_FILE" ]; then
  PARA_FLAGS=""
  [ "$THREAD_MODE" = true ] && PARA_FLAGS="$PARA_FLAGS --thread"
  [ "$SKIP_READS" = true ] && PARA_FLAGS="$PARA_FLAGS --skip-reads"
  [ -n "$RATE_LIMIT" ] && PARA_FLAGS="$PARA_FLAGS -r $RATE_LIMIT"
  PARA_FLAGS="$PARA_FLAGS -t $TIMEOUT"
  exec bash "$SCRIPT_DIR/parallel-tasks.sh" $PARA_FLAGS "$PARALLEL_FILE"
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
# Detect if Codex command includes --json for structured parsing
if [ "$IS_CODEX" = true ]; then
  case "$COMMAND" in
    *--json*|*--experimental-json*) IS_CODEX_JSON=true ;;
    *) IS_CODEX_JSON=false ;;
  esac
else
  IS_CODEX_JSON=false
fi

# Webhook
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WEBHOOK_URL=$(cat "$SCRIPT_DIR/.webhook-url" 2>/dev/null | tr -d '\n')
[ -z "$WEBHOOK_URL" ] && { echo "❌ Error: .webhook-url not found in $SCRIPT_DIR" >&2; echo "  Create it: echo 'https://discord.com/api/webhooks/ID/TOKEN' > $SCRIPT_DIR/.webhook-url" >&2; exit 1; }

# Validate webhook URL (GET returns 200 for valid webhooks)
if ! curl -s -o /dev/null -w "%{http_code}" "$WEBHOOK_URL" 2>/dev/null | grep -q "^200$"; then
  echo "❌ Error: Webhook URL appears invalid or unreachable" >&2
  echo "  Check: $SCRIPT_DIR/.webhook-url" >&2
  exit 1
fi

# Check unbuffer for Claude Code
if [ "$IS_CLAUDE" = true ] && ! command -v unbuffer &>/dev/null; then
  echo "❌ Error: 'unbuffer' not found (required for Claude Code streaming)" >&2
  echo "  Install: brew install expect (macOS) or apt install expect (Linux)" >&2
  exit 1
fi

# Bot token (optional, needed for --thread mode in text channels)
# Priority: CODECAST_BOT_TOKEN env var > macOS Keychain > .bot-token file
BOT_TOKEN="${CODECAST_BOT_TOKEN:-}"
if [ -z "$BOT_TOKEN" ] && command -v security &>/dev/null; then
  BOT_TOKEN=$(security find-generic-password -s discord-bot-token -a codecast -w 2>/dev/null || true)
fi
if [ -z "$BOT_TOKEN" ]; then
  BOT_TOKEN=$(cat "$SCRIPT_DIR/.bot-token" 2>/dev/null | tr -d '\n')
fi
if [ "$THREAD_MODE" = true ] && [ -z "$BOT_TOKEN" ]; then
  echo "⚠️  Warning: --thread requires a bot token for text channels" >&2
  echo "  Create: echo 'YOUR_BOT_TOKEN' > $SCRIPT_DIR/.bot-token" >&2
  echo "  Falling back to non-thread mode" >&2
  THREAD_MODE=false
fi

# Cleanup stale relay dirs (>7 days)
find /tmp -maxdepth 1 -name 'dev-relay.*' -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true

# Temp workspace
RELAY_DIR=$(mktemp -d /tmp/dev-relay.XXXXXX)
OUTPUT_FILE="$RELAY_DIR/output.log"
touch "$OUTPUT_FILE"

echo "📂 Relay: $RELAY_DIR"
echo "🚀 $AGENT_NAME | 📁 $WORKDIR | 🎯 $PLATFORM"

# --- Discord posting (used for start message from bash, before parser takes over) ---
post() {
  local msg="$1" name="${2:-$AGENT_NAME}"
  [ ${#msg} -gt 1950 ] && msg="${msg:0:1900}…*(truncated)*"
  local jmsg jname
  jmsg=$(python3 -c "import json,sys;print(json.dumps(sys.stdin.read()))" <<< "$msg")
  jname=$(python3 -c "import json;print(json.dumps('$name'))")
  curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"content\":${jmsg},\"username\":${jname}}" -o /dev/null 2>/dev/null || true
}

PARSER="$SCRIPT_DIR/parse-stream.py"

# --- Start ---
post "🚀 **${AGENT_NAME} Session Started**
\`\`\`
${COMMAND}
\`\`\`
📁 \`${WORKDIR}\` | ⏱️ ${TIMEOUT}s timeout"

cd "$WORKDIR"

# Write command to temp script to preserve quoting
CMD_FILE="$RELAY_DIR/cmd.sh"
printf '#!/bin/bash\ncd "%s"\n' "$WORKDIR" > "$CMD_FILE"
printf '%q ' "${COMMAND_ARGS[@]}" >> "$CMD_FILE"
printf '\n' >> "$CMD_FILE"
chmod +x "$CMD_FILE"

# Save session info (per-PID for concurrent session support)
SESSION_DIR="/tmp/dev-relay-sessions"
mkdir -p "$SESSION_DIR"
SESSION_FILE="$SESSION_DIR/$$.json"
cat > "$SESSION_FILE" <<EOF
{"pid":$$,"command":"$COMMAND","workdir":"$WORKDIR","agent":"$AGENT_NAME","relayDir":"$RELAY_DIR","platform":"$PLATFORM","startTime":"$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF

if [ "$IS_CLAUDE" = true ] || [ "$IS_CODEX_JSON" = true ]; then
  # Structured output: pipe through parse-stream.py
  # Claude Code: stream-json via unbuffer PTY
  # Codex: --json JSONL events (no unbuffer needed)
  export WEBHOOK_URL AGENT_NAME PLATFORM THREAD_MODE SKIP_READS BOT_TOKEN
  export RELAY_DIR
  [ -n "$RATE_LIMIT" ] && export CODECAST_RATE_LIMIT="$RATE_LIMIT"
  cd "$WORKDIR"
  if [ "$IS_CLAUDE" = true ]; then
    unbuffer bash "$CMD_FILE" 2>/dev/null | python3 "$PARSER" &
  else
    bash "$CMD_FILE" 2>/dev/null | python3 "$PARSER" &
  fi
  RELAY_PID=$!

  # Wait with timeout
  START=$(date +%s)
  while kill -0 "$RELAY_PID" 2>/dev/null; do
    NOW=$(date +%s)
    if [ $((NOW - START)) -ge "$TIMEOUT" ]; then
      post "⏰ **Timed out** after ${TIMEOUT}s"
      kill "$RELAY_PID" 2>/dev/null
      break
    fi
    sleep 5
  done
  wait "$RELAY_PID" 2>/dev/null
else
  # Non-Claude agents: use raw output relay with ANSI stripping
  script -q "$OUTPUT_FILE" "$CMD_FILE" &
  AGENT_PID=$!
  echo "$AGENT_PID" > "$RELAY_DIR/agent.pid"

  cleanup() {
    if kill -0 "$AGENT_PID" 2>/dev/null; then
      kill "$AGENT_PID" 2>/dev/null; sleep 1; kill -9 "$AGENT_PID" 2>/dev/null
    fi
  }
  trap cleanup EXIT

  START=$(date +%s)
  LAST_OUT_TIME=$START
  LAST_OFFSET=0
  HANG_WARNED=false

  while true; do
    NOW=$(date +%s)
    ELAPSED=$((NOW - START))
    [ "$ELAPSED" -ge "$TIMEOUT" ] && { post "⏰ **Timed out** after ${TIMEOUT}s"; kill "$AGENT_PID" 2>/dev/null; break; }

    ALIVE=true
    kill -0 "$AGENT_PID" 2>/dev/null || ALIVE=false

    FSIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || echo 0)
    if [ "$FSIZE" -gt "$LAST_OFFSET" ]; then
      LAST_OUT_TIME=$NOW; HANG_WARNED=false
      RAW=$(dd if="$OUTPUT_FILE" bs=1 skip="$LAST_OFFSET" count=$((FSIZE - LAST_OFFSET)) 2>/dev/null)
      LAST_OFFSET=$FSIZE
      CLEAN=$(echo "$RAW" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g; s/\x1b\][^\x07]*\x07//g; s/\r//g' | tr -d '\000' | head -c 1800)
      [ -n "$CLEAN" ] && post "\`\`\`\n${CLEAN}\n\`\`\`"
    fi

    if [ "$ALIVE" = false ]; then
      sleep 2
      FSIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || echo 0)
      if [ "$FSIZE" -gt "$LAST_OFFSET" ]; then
        RAW=$(dd if="$OUTPUT_FILE" bs=1 skip="$LAST_OFFSET" 2>/dev/null)
        CLEAN=$(echo "$RAW" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g; s/\r//g' | tr -d '\000' | head -c 1800)
        [ -n "$CLEAN" ] && post "\`\`\`\n${CLEAN}\n\`\`\`"
      fi
      wait "$AGENT_PID" 2>/dev/null; EC=$?
      M=$((ELAPSED / 60)); S=$((ELAPSED % 60))
      [ "$EC" -eq 0 ] && post "✅ **Completed** (exit: ${EC}, ${M}m${S}s)" || post "❌ **Ended** (exit: ${EC}, ${M}m${S}s)"
      break
    fi

    SILENT=$((NOW - LAST_OUT_TIME))
    if [ "$SILENT" -ge "$HANG_THRESHOLD" ] && [ "$HANG_WARNED" = false ]; then
      post "⚠️ **No output for ${SILENT}s** — may be stuck"; HANG_WARNED=true
    fi
    sleep "$INTERVAL"
  done
fi

# Post completion to Discord via webhook (most reliable — no OpenClaw middleman)
if [ -f "$SCRIPT_DIR/.webhook-url" ]; then
  WEBHOOK_URL=$(cat "$SCRIPT_DIR/.webhook-url")
  DURATION=$(($(date +%s) - $(date -j -f "%Y-%m-%dT%H:%M:%S" "${START_ISO%Z}" +%s 2>/dev/null || echo $SECONDS)))
  curl -s -H "Content-Type: application/json" \
    -d "{\"content\":\"✅ **Codecast session completed** — ${AGENT_NAME} finished in \`${WORKDIR}\` (${DURATION}s)\"}" \
    "$WEBHOOK_URL" >/dev/null 2>&1 || true
fi
# Also notify OpenClaw main session (fires on next heartbeat)
openclaw system event --text "Codecast done: ${AGENT_NAME} session finished in ${WORKDIR}" 2>/dev/null || true
rm -f "$SESSION_FILE" 2>/dev/null
echo "Done."
