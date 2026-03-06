#!/bin/bash
# deep-correct.sh
# Guided 3-level correction flow

if [ -z "$1" ]; then
  echo "Usage: $0 <error_description> [principle] [habit]"
  exit 1
fi

ERROR_DESC="$1"

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

echo "=== Deep Correction Flow ==="
echo "Surface Error: $ERROR_DESC"

SCRIPT_DIR=$(dirname "$0")

if [ -n "$2" ] && [ -n "$3" ]; then
  PRINCIPLE="$2"
  HABIT="$3"
else
  # Try LLM extraction (v1.1)
  echo "[LLM mode] Attempting extraction..."
  LLM_RESULT=$(python3 "$SCRIPT_DIR/llm_extract.py" "$ERROR_DESC" 2>/dev/null)
  
  if [ "$LLM_RESULT" = "FALLBACK" ] || [ -z "$LLM_RESULT" ]; then
    echo "[offline mode] LLM extraction unavailable or failed. Falling back to manual input."
    echo "Enter Principle (what underlying rule was violated): "
    read -r PRINCIPLE
    echo "Enter Habit (what behavioral change prevents recurrence): "
    read -r HABIT
  else
    # Parse JSON
    ERROR_DESC=$(echo "$LLM_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get(\"surface\", \"\"))")
    PRINCIPLE=$(echo "$LLM_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get(\"principle\", \"\"))")
    HABIT=$(echo "$LLM_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get(\"habit\", \"\"))")
    
    echo ""
    echo "LLM Extracted Levels:"
    echo "Surface: $ERROR_DESC"
    echo "Principle: $PRINCIPLE"
    echo "Habit: $HABIT"
    echo ""
    echo "Press Enter to confirm and save, or Ctrl+C to abort."
    read -r _
  fi
fi

DATE=$(date +%Y-%m-%d)

cat <<INNEREOF >> "$LEARNINGS_FILE"

## [$DATE] Deep Correction
**Surface Error:** $ERROR_DESC
**Principle:** $PRINCIPLE
**Habit:** $HABIT

INNEREOF

echo "✅ Saved to $LEARNINGS_FILE"
echo "Summary:"
echo "- Surface: $ERROR_DESC"
echo "- Principle: $PRINCIPLE"
echo "- Habit: $HABIT"
