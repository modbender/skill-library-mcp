#!/bin/bash
# success-capture.sh
# Capture what worked + why

# Dynamic workspace detection — works for any OpenClaw user
WORKSPACE=$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null)
if [ -z "$WORKSPACE" ]; then
  WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
fi

# Try self-improving-agent first, fallback to metaskill's own learnings
if [ -f "$WORKSPACE/skills/self-improving-agent/.learnings/LEARNINGS.md" ]; then
  LEARNINGS_FILE="$WORKSPACE/skills/self-improving-agent/.learnings/LEARNINGS.md"
else
  # Fallback: use metaskill's own learnings dir
  mkdir -p "$WORKSPACE/skills/metaskill/.learnings"
  LEARNINGS_FILE="$WORKSPACE/skills/metaskill/.learnings/LEARNINGS.md"
  # Create file if not exists
  [ -f "$LEARNINGS_FILE" ] || echo -e "# Learnings Log\n\n---\n" > "$LEARNINGS_FILE"
fi

WINS_FILE="$WORKSPACE/skills/metaskill/.learnings/WINS.md"
mkdir -p "$(dirname "$WINS_FILE")"

if [ -z "$1" ]; then
  echo "Usage: $0 <what_worked> [why_it_worked] or $0 --summary"
  exit 1
fi

# If running in summary mode:
if [ "$1" == "--summary" ]; then
    WINS=$(grep -c "^##" "$WINS_FILE" 2>/dev/null || echo 0)
    ERRORS=$(grep -c "^##" "$LEARNINGS_FILE" 2>/dev/null || echo 0)
    echo "=== Weekly Summary ==="
    echo "Wins logged: $WINS"
    echo "Deep Corrections (Errors): $ERRORS"
    exit 0
fi

WHAT="$1"
WHY="$2"

DATE=$(date +%Y-%m-%d)

cat <<INNEREOF >> "$WINS_FILE"

## [$DATE] Win
**What worked:** $WHAT
**Why it worked:** ${WHY:-"Not specified"}

INNEREOF

echo "✅ Success captured to $WINS_FILE"
