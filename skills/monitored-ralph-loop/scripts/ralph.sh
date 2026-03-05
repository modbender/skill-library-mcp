#!/usr/bin/env bash
#
# Ralph Loop - Event-Driven AI Agent Loop
# https://github.com/Endogen/ralph-loop
#
set -euo pipefail

# Defaults
MAX_ITERS=${1:-20}
CLI="${RALPH_CLI:-codex}"
# CLI-specific default flags
if [[ -z "${RALPH_FLAGS:-}" ]]; then
  case "${CLI}" in
    codex)  CLI_FLAGS="-s workspace-write" ;;
    claude) CLI_FLAGS="--dangerously-skip-permissions" ;;
    *)      CLI_FLAGS="" ;;
  esac
else
  CLI_FLAGS="${RALPH_FLAGS}"
fi
TEST_CMD="${RALPH_TEST:-}"
PLAN_FILE="IMPLEMENTATION_PLAN.md"
LOG_DIR=".ralph"
LOG_FILE="$LOG_DIR/ralph.log"
NOTIFY_FILE="$LOG_DIR/pending-notification.txt"

# Completion markers
PLANNING_DONE="STATUS: PLANNING_COMPLETE"
BUILDING_DONE="STATUS: COMPLETE"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
  cat << EOF
Usage: $(basename "$0") [max_iterations]

Environment variables:
  RALPH_CLI    - CLI to use (codex, claude, opencode, goose) [default: codex]
  RALPH_FLAGS  - CLI flags [default: auto-detected per CLI]
  RALPH_TEST   - Test command to run after each iteration [optional]

Examples:
  ./ralph.sh 20                          # Run 20 iterations with Codex
  RALPH_CLI=claude ./ralph.sh 10         # Use Claude Code
  RALPH_TEST="pytest" ./ralph.sh         # Run pytest after each iteration
EOF
  exit 1
}

[[ "${1:-}" == "-h" || "${1:-}" == "--help" ]] && usage

# Setup
mkdir -p "$LOG_DIR"

log() {
  echo -e "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Send notification via OpenClaw cron + write details to file
# The orchestrating agent (OpenClaw) will triage and decide whether to
# forward to human or attempt to help.
notify() {
  local prefix="$1"
  local message="$2"
  local details="${3:-}"
  local timestamp
  timestamp="$(date -Iseconds)"
  local project_dir
  project_dir="$(pwd)"
  local project_name
  project_name="$(basename "$project_dir")"
  
  # Write detailed notification for the orchestrating agent to triage
  cat > "$NOTIFY_FILE" << EOF
{
  "timestamp": "$timestamp",
  "project": "$project_dir",
  "project_name": "$project_name",
  "prefix": "$prefix",
  "message": "$message",
  "details": "$details",
  "iteration": ${CURRENT_ITER:-0},
  "max_iterations": $MAX_ITERS,
  "cli": "$CLI",
  "log_tail": "$(tail -50 "$LOG_FILE" 2>/dev/null | base64 -w0)",
  "status": "pending"
}
EOF
  
  log "📝 Notification written to $NOTIFY_FILE"
  
  # Trigger OpenClaw via cron CLI (properly initializes scheduler state)
  if command -v openclaw &>/dev/null; then
    local event_text="[Ralph:${project_name}] ${prefix}: ${message}"
    if openclaw cron add \
      --name "ralph-${project_name}-notify" \
      --at "5s" \
      --session main \
      --system-event "$event_text" \
      --wake now \
      --delete-after-run >/dev/null 2>&1; then
      sed -i 's/"status": "pending"/"status": "delivered"/' "$NOTIFY_FILE" 2>/dev/null || true
      log "✅ OpenClaw notification scheduled"
    else
      log "⚠️ OpenClaw cron failed - notification saved to file for heartbeat pickup"
    fi
  else
    log "📋 openclaw not found - notification saved to $NOTIFY_FILE"
  fi
}

# Preflight checks
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo -e "${RED}❌ Must run inside a git repository${NC}"
  exit 1
fi

if ! command -v "$CLI" &>/dev/null; then
  echo -e "${RED}❌ CLI not found: $CLI${NC}"
  exit 1
fi

if [[ ! -f "PROMPT.md" ]]; then
  echo -e "${YELLOW}⚠️ PROMPT.md not found. Creating template...${NC}"
  cat > PROMPT.md << 'EOF'
# Ralph Loop

## Goal
[Describe what you want to build]

## Context
- Read: specs/*.md, IMPLEMENTATION_PLAN.md, AGENTS.md

## Notifications
When you need input or hit a blocker, write to .ralph/pending-notification.txt:
```bash
mkdir -p .ralph
cat > .ralph/pending-notification.txt << 'NOTIFY'
{"prefix":"ERROR","message":"Brief description","details":"Full context..."}
NOTIFY
```

Prefixes:
- DECISION: Need human input on a choice
- ERROR: Tests failing after retries  
- BLOCKED: Missing dependency or unclear spec
- PROGRESS: Major milestone complete
- DONE: All tasks finished

## Completion
When finished, add to IMPLEMENTATION_PLAN.md: STATUS: COMPLETE
EOF
  echo -e "${BLUE}📝 Created PROMPT.md template. Edit it and run again.${NC}"
  exit 0
fi

touch AGENTS.md "$PLAN_FILE" 2>/dev/null || true

# Clear any stale pending notification from previous run
[[ -f "$NOTIFY_FILE" ]] && rm -f "$NOTIFY_FILE"

echo -e "${BLUE}🐺 Ralph Loop starting${NC}"
echo -e "   CLI: $CLI $CLI_FLAGS"
echo -e "   Max iterations: $MAX_ITERS"
echo -e "   Project: $(pwd)"
[[ -n "$TEST_CMD" ]] && echo -e "   Test command: $TEST_CMD"
echo ""

# Main loop
for i in $(seq 1 "$MAX_ITERS"); do
  CURRENT_ITER=$i
  export CURRENT_ITER
  
  log "${BLUE}=== Iteration $i/$MAX_ITERS ===${NC}"
  
  # Build the command based on CLI
  case "$CLI" in
    codex)
      CMD="codex exec $CLI_FLAGS"
      ;;
    claude)
      CMD="claude --print $CLI_FLAGS"
      ;;
    opencode)
      CMD="opencode run"
      ;;
    goose)
      CMD="goose run"
      ;;
    *)
      CMD="$CLI $CLI_FLAGS"
      ;;
  esac
  
  # Run the agent (fresh session each time!)
  log "Running: $CMD \"...\""
  if ! $CMD "$(cat PROMPT.md)" 2>&1 | tee -a "$LOG_FILE"; then
    EXIT_CODE=$?
    log "${YELLOW}⚠️ Agent exited with code $EXIT_CODE${NC}"
    notify "ERROR" "Agent crashed on iteration $i/$MAX_ITERS" "Exit code: $EXIT_CODE. Check log for details."
    sleep 5
    continue
  fi
  
  # Run tests if configured
  if [[ -n "$TEST_CMD" ]]; then
    log "Running tests: $TEST_CMD"
    if bash -lc "$TEST_CMD" 2>&1 | tee -a "$LOG_FILE"; then
      log "${GREEN}✅ Tests passed${NC}"
    else
      log "${YELLOW}⚠️ Tests failed${NC}"
    fi
  fi
  
  # Check completion markers
  if grep -Fq "$BUILDING_DONE" "$PLAN_FILE" 2>/dev/null; then
    log "${GREEN}✅ All tasks complete!${NC}"
    notify "DONE" "All tasks complete" "Ralph loop finished successfully."
    exit 0
  fi
  
  if grep -Fq "$PLANNING_DONE" "$PLAN_FILE" 2>/dev/null; then
    log "${GREEN}📋 Planning phase complete${NC}"
    notify "PLANNING_COMPLETE" "Ready for BUILDING mode" "Switch PROMPT.md to PROMPT-BUILDING.md and restart."
    exit 0
  fi
  
  # Brief pause between iterations
  sleep 2
done

log "${RED}❌ Max iterations ($MAX_ITERS) reached${NC}"
notify "BLOCKED" "Max iterations reached" "Completed $MAX_ITERS iterations without finishing. Manual review needed."
exit 1
