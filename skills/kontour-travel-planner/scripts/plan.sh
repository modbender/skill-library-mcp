#!/usr/bin/env bash
# Kontour Travel Planner — Quick Planning Script
# Usage: ./plan.sh "your trip description"
# Outputs structured trip context JSON by extracting dimensions from natural language.

set -euo pipefail

QUERY="${1:-}"
if [ -z "$QUERY" ]; then
  echo "Usage: $0 \"<trip description>\""
  echo "Example: $0 \"2 weeks in Japan for a couple, mid-range budget, food and temples\""
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Extract dimensions using pattern matching
extract_destination() {
  echo "$1" | grep -oiE '\b(in|to|visit|visiting|explore|exploring)\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)*' | head -1 | sed 's/^[a-z]* //' | sed 's/ [Ff]or$//'
}

extract_duration() {
  local dur
  dur=$(echo "$1" | grep -oiE '\b(\d+)\s*(days?|weeks?|nights?)' | head -1)
  if [ -n "$dur" ]; then
    local num=$(echo "$dur" | grep -oE '[0-9]+')
    if echo "$dur" | grep -qi 'week'; then
      echo $((num * 7))
    else
      echo "$num"
    fi
  fi
}

extract_travelers() {
  local t="$1"
  if echo "$t" | grep -qi 'solo'; then echo 1
  elif echo "$t" | grep -qi 'couple'; then echo 2
  elif echo "$t" | grep -qi 'family'; then echo 4
  else
    local num=$(echo "$t" | grep -oiE '(\d+)\s*(people|travelers|adults|persons)' | grep -oE '[0-9]+' | head -1)
    echo "${num:-}"
  fi
}

extract_budget_tier() {
  local t="$1"
  if echo "$t" | grep -qi 'mid.range\|mid-range\|moderate\|comfort'; then echo "mid"
  elif echo "$t" | grep -qi 'budget\|cheap\|backpack'; then echo "budget"
  elif echo "$t" | grep -qi 'luxury\|premium\|high.end\|splurge'; then echo "luxury"
  fi
}

extract_interests() {
  local interests=()
  local t="$(echo "$1" | tr '[:upper:]' '[:lower:]')"
  for kw in food culinary temple culture history museum art beach adventure hiking nature nightlife shopping wellness spa photography architecture wine; do
    if echo "$t" | grep -q "$kw"; then
      interests+=("\"$kw\"")
    fi
  done
  local IFS=","
  echo "[${interests[*]:-}]"
}

DEST=$(extract_destination "$QUERY")
DURATION=$(extract_duration "$QUERY")
TRAVELERS=$(extract_travelers "$QUERY")
BUDGET_TIER=$(extract_budget_tier "$QUERY")
INTERESTS=$(extract_interests "$QUERY")

# Look up destination in references
DEST_DATA=""
if [ -n "$DEST" ] && [ -f "$SKILL_DIR/references/destinations.json" ]; then
  DEST_LOWER=$(echo "$DEST" | tr '[:upper:]' '[:lower:]')
  DEST_DATA=$(python3 -c "
import json, sys
with open('$SKILL_DIR/references/destinations.json') as f:
    dests = json.load(f)
match = next((d for d in dests if d['name'].lower() == '$DEST_LOWER' or d['country'].lower() == '$DEST_LOWER'), None)
if match:
    print(json.dumps({'name': match['name'], 'country': match['country'], 'coordinates': match['coordinates'], 'currency': match['currency'], 'timezone': match['timezone'], 'avg_daily_cost_usd': match['avg_daily_cost_usd']}))
" 2>/dev/null || true)
fi

# Build JSON output
python3 -c "
import json

ctx = {}

dest = '''$DEST'''.strip()
if dest:
    ctx['destination'] = {'name': dest}

dest_data = '''$DEST_DATA'''.strip()
if dest_data:
    dd = json.loads(dest_data)
    ctx['destination'] = dd

duration = '''$DURATION'''.strip()
if duration:
    ctx['duration_days'] = int(duration)

travelers = '''$TRAVELERS'''.strip()
if travelers:
    ctx['travelers'] = {'adults': int(travelers)}

tier = '''$BUDGET_TIER'''.strip()
if tier:
    ctx['budget'] = {'tier': tier}
    if dest_data:
        dd = json.loads(dest_data)
        costs = dd.get('avg_daily_cost_usd', {})
        daily = costs.get(tier, costs.get('mid'))
        if daily and duration:
            ctx['budget']['estimated_total'] = daily * int(duration) * (int(travelers) if travelers else 1)
            ctx['budget']['daily_per_person'] = daily

interests = json.loads('''$INTERESTS''')
if interests:
    ctx['interests'] = interests

ctx['planning_stage'] = 'discover'
dims_complete = sum(1 for v in [dest, duration, travelers, tier, interests] if v)
if dims_complete >= 4:
    ctx['planning_stage'] = 'develop'
if dims_complete >= 6:
    ctx['planning_stage'] = 'refine'

ctx['open_decisions'] = []
if not dest: ctx['open_decisions'].append('destination')
if not duration: ctx['open_decisions'].append('dates/duration')
if not travelers: ctx['open_decisions'].append('travelers')
if not tier: ctx['open_decisions'].append('budget')
if not interests: ctx['open_decisions'].append('interests')
ctx['open_decisions'].extend(['accommodation', 'transport', 'constraints'])

print(json.dumps(ctx, indent=2))
"
