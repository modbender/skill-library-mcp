#!/bin/bash
# parallel-tasks.sh — Run multiple codecast sessions across git worktrees
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
#   -r <n>         Rate limit per task (default: 25)
#   -a <agent>     Agent: claude (default), codex
#   --thread       Each task gets its own Discord thread
#   --skip-reads   Hide Read events
#   --worktree     Use git worktrees instead of separate repos
#
# Each task runs in its own relay session. All post to the same Discord channel
# but in separate threads (when --thread is used). A summary message is posted
# when all tasks complete.

set -uo pipefail

TIMEOUT=1800
RATE_LIMIT=""
AGENT="claude"
THREAD_MODE=false
SKIP_READS=false
USE_WORKTREE=false

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Parse options
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --thread)     THREAD_MODE=true; shift ;;
    --skip-reads) SKIP_READS=true; shift ;;
    --worktree)   USE_WORKTREE=true; shift ;;
    -t) TIMEOUT="$2"; shift 2 ;;
    -r) RATE_LIMIT="$2"; shift 2 ;;
    -a) AGENT="$2"; shift 2 ;;
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
  # Skip comments and empty lines
  line=$(echo "$line" | sed 's/#.*//' | xargs)
  [ -z "$line" ] && continue

  # Parse: dir | prompt
  TASK_DIR=$(echo "$line" | cut -d'|' -f1 | xargs)
  TASK_PROMPT=$(echo "$line" | cut -d'|' -f2- | xargs)

  [ -z "$TASK_DIR" ] || [ -z "$TASK_PROMPT" ] && {
    echo "⚠️  Skipping invalid line: $line" >&2
    continue
  }

  # Expand ~ in path
  TASK_DIR="${TASK_DIR/#\~/$HOME}"

  TASK_DIRS+=("$TASK_DIR")
  TASK_PROMPTS+=("$TASK_PROMPT")
  TASK_NAMES+=("$(basename "$TASK_DIR")")
  TASK_COUNT=$((TASK_COUNT + 1))
done < "$TASKS_FILE"

[ "$TASK_COUNT" -eq 0 ] && { echo "❌ Error: No valid tasks found in $TASKS_FILE" >&2; exit 1; }

echo "🚀 Starting $TASK_COUNT parallel codecast sessions"
echo "  Agent: $AGENT | Timeout: ${TIMEOUT}s | Thread: $THREAD_MODE"
echo ""

# Webhook for summary message
WEBHOOK_URL=$(cat "$SCRIPT_DIR/.webhook-url" 2>/dev/null | tr -d '\n')

post_summary() {
  local msg="$1"
  [ ${#msg} -gt 1950 ] && msg="${msg:0:1900}…*(truncated)*"
  local jmsg
  jmsg=$(python3 -c "import json,sys;print(json.dumps(sys.stdin.read()))" <<< "$msg")
  curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"content\":${jmsg},\"username\":\"Codecast Parallel\"}" -o /dev/null 2>/dev/null || true
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
    WT_DIR="/tmp/codecast-wt-${TASK_NAME}-$$"
    BRANCH="codecast-${TASK_NAME}-$$"
    (cd "$TASK_DIR" && git worktree add "$WT_DIR" -b "$BRANCH" HEAD 2>/dev/null)
    if [ $? -eq 0 ]; then
      WORK_DIR="$WT_DIR"
      echo "  📂 Worktree: $WT_DIR (branch: $BRANCH)"
    else
      echo "  ⚠️  Worktree failed for $TASK_NAME, using original dir" >&2
    fi
  fi

  # Build agent command
  COMPLETION_MSG="When completely finished, run: openclaw system event --text 'Done: ${TASK_NAME} - task complete' --mode now"
  case "$AGENT" in
    claude*)
      AGENT_CMD="claude -p --dangerously-skip-permissions --output-format stream-json --verbose '${TASK_PROMPT}. ${COMPLETION_MSG}'"
      ;;
    codex*)
      AGENT_CMD="codex exec --json --full-auto '${TASK_PROMPT}. ${COMPLETION_MSG}'"
      ;;
    *)
      AGENT_CMD="${AGENT} '${TASK_PROMPT}'"
      ;;
  esac

  # Build relay flags
  RELAY_FLAGS="-w $WORK_DIR -t $TIMEOUT -n '${AGENT} [$TASK_NAME]'"
  # Always use threads for parallel so tasks don't interleave
  RELAY_FLAGS="$RELAY_FLAGS --thread"
  [ "$SKIP_READS" = true ] && RELAY_FLAGS="$RELAY_FLAGS --skip-reads"
  [ -n "$RATE_LIMIT" ] && RELAY_FLAGS="$RELAY_FLAGS -r $RATE_LIMIT"

  echo "  🚀 Task $((i + 1))/$TASK_COUNT: $TASK_NAME"

  # Launch in background
  eval "bash '$SCRIPT_DIR/dev-relay.sh' $RELAY_FLAGS -- $AGENT_CMD" &
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
  wait "${PIDS[$i]}" 2>/dev/null
  EC=$?
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
    WT_DIR="/tmp/codecast-wt-${TASK_NAME}-$$"
    BRANCH="codecast-${TASK_NAME}-$$"
    if [ -d "$WT_DIR" ]; then
      (cd "$TASK_DIR" && git worktree remove "$WT_DIR" --force 2>/dev/null)
      (cd "$TASK_DIR" && git branch -D "$BRANCH" 2>/dev/null)
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
