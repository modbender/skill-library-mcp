#!/bin/bash
# transfer-check.sh
# Pre-task analogy lookup

if [ -z "$1" ]; then
  echo "Usage: $0 <task_description>"
  exit 1
fi

TASK="$1"

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

echo "=== Transfer Learning Check ==="
echo "Task: $TASK"

if [ ! -f "$LEARNINGS_FILE" ]; then
  echo "No analogous patterns — proceed, but log what works"
  exit 0
fi

SCRIPT_DIR=$(dirname "$0")
echo "Searching for analogous principles..."

# Try LLM extraction (v1.1)
echo "[LLM mode] Searching for analogies..."
LLM_RESULT=$(python3 "$SCRIPT_DIR/llm_transfer.py" "$TASK" "$LEARNINGS_FILE" 2>/dev/null)

if [ "$LLM_RESULT" = "FALLBACK" ] || [ -z "$LLM_RESULT" ]; then
  echo "[offline mode] LLM search unavailable or failed. Falling back to naive keyword search."
  
  # Extract naive keywords (simple lowercase, remove common words)
  KEYWORDS=$(echo "$TASK" | tr "[:upper:]" "[:lower:]" | sed -E "s/( a | the | to | and | for | in | of | on | with )/ /g" | tr -s " ")

  MATCHES=""
  for word in $KEYWORDS; do
    if [ ${#word} -gt 3 ]; then
      FOUND=$(grep -i -C 2 "$word" "$LEARNINGS_FILE" 2>/dev/null)
      if [ ! -z "$FOUND" ]; then
        MATCHES="$MATCHES\n$FOUND"
      fi
    fi
  done

  if [ -z "$MATCHES" ] || [ "$MATCHES" = "\n" ]; then
    echo "No analogous patterns — proceed, but log what works"
  else
    echo "Relevant principles found:"
    echo -e "$MATCHES" | sort -u | head -n 15
  fi
else
  # Parse JSON
  # Check if "principles" key exists
  HAS_PRINCIPLES=$(echo "$LLM_RESULT" | python3 -c "import sys, json; print('1' if json.load(sys.stdin).get('principles', []) else '0')")
  
  if [ "$HAS_PRINCIPLES" = "1" ]; then
    echo "Relevant principles found (LLM Analogy):"
    echo "$LLM_RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data.get('principles', []):
    print(f'- Principle: {p.get(\"principle\", \"\")}')
    print(f'  Reasoning: {p.get(\"reasoning\", \"\")}')
    print()
"
  else
    echo "No analogous patterns found by LLM — proceed, but log what works"
  fi
fi
