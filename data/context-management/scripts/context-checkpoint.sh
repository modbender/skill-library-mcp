#!/usr/bin/env bash
# context-checkpoint.sh — Write or read context checkpoint files
# Usage:
#   context-checkpoint.sh write <workspace_root> [task] [state] [decisions] [files_changed] [next_steps]
#   context-checkpoint.sh read  <workspace_root>
#   context-checkpoint.sh clear <workspace_root>
set -euo pipefail

ACTION="${1:-help}"
WORKSPACE="${2:-.}"
CHECKPOINT="$WORKSPACE/.context-checkpoint.md"

case "$ACTION" in
  write)
    TASK="${3:-No active task described}"
    STATE="${4:-No state captured}"
    DECISIONS="${5:-None recorded}"
    FILES="${6:-None recorded}"
    NEXT="${7:-No next steps defined}"
    DATE=$(date -u +"%Y-%m-%d %H:%M UTC")

    cat > "$CHECKPOINT" <<EOF
# Context Checkpoint — $DATE

## Active Task
$TASK

## Key State
$STATE

## Decisions Made This Session
$DECISIONS

## Files Changed
$FILES

## Next Steps
$NEXT
EOF
    echo "Checkpoint written: $CHECKPOINT"
    ;;

  read)
    if [ -f "$CHECKPOINT" ]; then
      cat "$CHECKPOINT"
    else
      echo "No checkpoint found at $CHECKPOINT"
      exit 1
    fi
    ;;

  clear)
    if [ -f "$CHECKPOINT" ]; then
      rm "$CHECKPOINT"
      echo "Checkpoint cleared: $CHECKPOINT"
    else
      echo "No checkpoint to clear"
    fi
    ;;

  help|--help|-h)
    echo "Usage: context-checkpoint.sh {write|read|clear} <workspace_root> [task] [state] [decisions] [files_changed] [next_steps]"
    echo ""
    echo "Actions:"
    echo "  write  Write a checkpoint file before compaction or /new"
    echo "  read   Read existing checkpoint (for post-compaction recovery)"
    echo "  clear  Remove checkpoint after consuming it"
    echo ""
    echo "For complex content, write the checkpoint file directly instead of"
    echo "using this script — multiline content doesn't work well as arguments."
    ;;

  *)
    echo "Unknown action: $ACTION" >&2
    echo "Usage: context-checkpoint.sh {write|read|clear} <workspace_root>" >&2
    exit 1
    ;;
esac
