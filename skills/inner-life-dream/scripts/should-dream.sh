#!/usr/bin/env bash
# inner-life-dream: Gate logic for dreaming
# Returns a topic on stdout if dreaming should happen, exits non-zero otherwise.
# Usage: DREAM_TOPIC=$(./should-dream.sh) && echo "Dream: $DREAM_TOPIC" || echo "No dream"

set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
DATA_DIR="$WORKSPACE/data"
MEMORY_DIR="$WORKSPACE/memory"
STATE_FILE="$DATA_DIR/dream-state.json"
CONFIG_FILE="$DATA_DIR/dream-config.json"

# Check: inner-life-core must be initialized
if [ ! -f "$MEMORY_DIR/inner-state.json" ]; then
  echo "ERROR: inner-life-core not initialized. Run: bash skills/inner-life-core/scripts/init.sh" >&2
  exit 1
fi
if [ ! -d "$MEMORY_DIR/dreams" ]; then
  echo "ERROR: memory/dreams/ directory missing. Run: bash skills/inner-life-core/scripts/init.sh" >&2
  exit 1
fi

# Defaults
QUIET_START=23  # 11 PM
QUIET_END=7     # 7 AM

DEFAULT_TOPICS=(
  "future:What could this project or capability become in 6 months?"
  "tangent:An interesting technology or concept worth exploring"
  "strategy:Long-term thinking about goals and direction"
  "creative:A wild idea that might be crazy or brilliant"
  "reflection:Looking back at recent work — what patterns emerge?"
  "hypothetical:A what-if scenario worth thinking through"
  "connection:Unexpected links between different domains or ideas"
)

# Ensure data dir exists
mkdir -p "$DATA_DIR"

# Initialize state if missing
if [ ! -f "$STATE_FILE" ]; then
  cat > "$STATE_FILE" << 'EOF'
{"lastDreamDate":"","dreamsTonight":0,"maxDreamsPerNight":1,"dreamChance":1.0}
EOF
fi

# Read state
LAST_DATE=$(jq -r '.lastDreamDate' "$STATE_FILE")
DREAMS_TONIGHT=$(jq -r '.dreamsTonight' "$STATE_FILE")
MAX_DREAMS=$(jq -r '.maxDreamsPerNight' "$STATE_FILE")
DREAM_CHANCE=$(jq -r '.dreamChance' "$STATE_FILE")

# Validate DREAM_CHANCE is a number (prevent code injection)
if ! [[ "$DREAM_CHANCE" =~ ^[0-9]*\.?[0-9]+$ ]]; then
  echo "WARNING: Invalid dreamChance value '$DREAM_CHANCE', defaulting to 1.0" >&2
  DREAM_CHANCE="1.0"
fi

# Check 1: Are we in quiet hours?
HOUR=$(date +%H | sed 's/^0//')
if [ "$QUIET_START" -gt "$QUIET_END" ]; then
  # Wraps midnight (e.g., 23-7)
  if [ "$HOUR" -lt "$QUIET_END" ] || [ "$HOUR" -ge "$QUIET_START" ]; then
    : # In quiet hours
  else
    exit 1
  fi
else
  if [ "$HOUR" -ge "$QUIET_START" ] && [ "$HOUR" -lt "$QUIET_END" ]; then
    : # In quiet hours
  else
    exit 1
  fi
fi

# Check 2: Have we hit the nightly limit?
TODAY=$(date +%Y-%m-%d)
if [ "$LAST_DATE" = "$TODAY" ] && [ "$DREAMS_TONIGHT" -ge "$MAX_DREAMS" ]; then
  exit 1
fi

# Check 3: Roll dice
ROLL=$(python3 -c "import sys,random; print(1 if random.random() < float(sys.argv[1]) else 0)" "$DREAM_CHANCE" 2>/dev/null || echo "1")
if [ "$ROLL" != "1" ]; then
  exit 1
fi

# All checks passed — pick a topic

# Load custom topics if available
if [ -f "$CONFIG_FILE" ]; then
  TOPIC_COUNT=$(jq '.topics | length' "$CONFIG_FILE")
  if [ "$TOPIC_COUNT" -gt 0 ]; then
    IDX=$(( RANDOM % TOPIC_COUNT ))
    TOPIC=$(jq -r ".topics[$IDX]" "$CONFIG_FILE")
  fi
fi

# Fall back to defaults
if [ -z "${TOPIC:-}" ]; then
  IDX=$(( RANDOM % ${#DEFAULT_TOPICS[@]} ))
  TOPIC="${DEFAULT_TOPICS[$IDX]}"
fi

# Check for dream-topic signal in daily notes
DAILY_NOTE="$MEMORY_DIR/$(date +%Y-%m-%d).md"
if [ -f "$DAILY_NOTE" ]; then
  SIGNAL=$(grep -oP '<!-- dream-topic: \K[^>]+(?= -->)' "$DAILY_NOTE" 2>/dev/null | tail -1 || true)
  if [ -n "$SIGNAL" ]; then
    TOPIC="signal:$SIGNAL"
  fi
fi

# Update state
if [ "$LAST_DATE" = "$TODAY" ]; then
  NEW_COUNT=$((DREAMS_TONIGHT + 1))
else
  NEW_COUNT=1
fi

tmp=$(jq --arg date "$TODAY" --argjson count "$NEW_COUNT" \
  '.lastDreamDate = $date | .dreamsTonight = $count' "$STATE_FILE")
echo "$tmp" > "$STATE_FILE"

# Output topic
echo "$TOPIC"
