#!/usr/bin/env bash
# Start a Claude Code task in a tmux session
# Usage: start.sh --label <name> --workdir <path> [--task <prompt>] [--task-file <file>] [--mode <plan|auto>] [--model <model>]

set -euo pipefail

LABEL=""
WORKDIR=""
TASK=""
TASK_FILE=""
MODE="auto"
MODEL=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --label) LABEL="$2"; shift 2;;
    --workdir) WORKDIR="$2"; shift 2;;
    --task) TASK="$2"; shift 2;;
    --task-file) TASK_FILE="$2"; shift 2;;
    --mode) MODE="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    *) echo "Unknown option: $1"; exit 1;;
  esac
done

if [[ -z "$LABEL" || -z "$WORKDIR" ]]; then
  echo "Usage: start.sh --label <name> --workdir <path> [--task <prompt>] [--task-file <file>] [--mode plan|auto] [--model <model>]"
  exit 1
fi

SESSION="cc-${LABEL}"

# Load task from file if specified
if [[ -n "$TASK_FILE" && -f "$TASK_FILE" ]]; then
  TASK=$(cat "$TASK_FILE")
fi

# Guard: must have a task
if [[ -z "$TASK" ]]; then
  echo "Error: --task or --task-file required (otherwise Claude Code starts with no input)"
  exit 1
fi

# Kill existing session if any
tmux -L cc kill-session -t "$SESSION" 2>/dev/null || true

# Build claude command
CLAUDE_CMD="claude"
case $MODE in
  plan) CLAUDE_CMD="$CLAUDE_CMD --permission-mode plan";;
  auto) CLAUDE_CMD="$CLAUDE_CMD --dangerously-skip-permissions";;
  *) echo "Unknown mode: $MODE"; exit 1;;
esac

# ⚠️  auto mode uses --dangerously-skip-permissions: Claude Code runs all tools
# without confirmation. Only use in trusted environments with version-controlled code.

if [[ -n "$MODEL" ]]; then
  CLAUDE_CMD="$CLAUDE_CMD --model $MODEL"
fi

# Create tmux session
tmux -L cc new-session -d -s "$SESSION" -c "$WORKDIR"
sleep 0.5

# Start claude in interactive mode
tmux -L cc send-keys -t "$SESSION" "$CLAUDE_CMD" Enter
sleep 3

# Send task via temp file + tmux load-buffer to handle multi-line safely
TMPFILE=$(mktemp /tmp/cc-task-XXXXXX.txt)
printf '%s' "$TASK" > "$TMPFILE"
tmux -L cc load-buffer "$TMPFILE"
tmux -L cc paste-buffer -t "$SESSION"
rm -f "$TMPFILE"
sleep 0.3
tmux -L cc send-keys -t "$SESSION" Enter

echo "✅ Session started: $SESSION"
echo "📂 Workdir: $WORKDIR"
echo "🔧 Mode: $MODE"
echo "⚠️  Permissions: $([ "$MODE" = "auto" ] && echo "SKIPPED (auto mode)" || echo "plan mode")"
echo "👁️ Attach: tmux -L cc attach -t $SESSION"
echo "📋 Monitor: $(dirname "$0")/monitor.sh --session $SESSION"
