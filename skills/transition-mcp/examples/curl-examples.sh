#!/usr/bin/env bash
# Transition API — curl examples
# Requires: TRANSITION_API_KEY environment variable (for authenticated endpoints)

set -euo pipefail

BASE="https://api.transition.fun"
KEY="${TRANSITION_API_KEY:-}"

# ─── Free (no auth) ──────────────────────────────────────────────────────────

echo "=== Workout of the Day (no auth required) ==="
curl -s "$BASE/api/v1/wod?sport=run&duration=45" | jq .

echo ""
echo "=== Swim WOD, 30 minutes ==="
curl -s "$BASE/api/v1/wod?sport=swim&duration=30" | jq .

# ─── Authenticated ───────────────────────────────────────────────────────────

if [ -z "$KEY" ]; then
  echo ""
  echo "Set TRANSITION_API_KEY to run authenticated examples."
  echo "  export TRANSITION_API_KEY=tr_live_xxxxxxxxxxxxxxxxxxxxx"
  exit 0
fi

echo ""
echo "=== This Week's Workouts ==="
START=$(date +%Y-%m-%d)
END=$(date -v+6d +%Y-%m-%d 2>/dev/null || date -d "+6 days" +%Y-%m-%d)
curl -s -H "X-API-Key: $KEY" "$BASE/api/v1/workouts?start=$START&end=$END" | jq .

echo ""
echo "=== Performance Stats ==="
curl -s -H "X-API-Key: $KEY" "$BASE/api/v1/performance/stats" | jq .

echo ""
echo "=== PMC (Fitness/Fatigue/Form) ==="
curl -s -H "X-API-Key: $KEY" "$BASE/api/v1/performance/pmc" | jq .

echo ""
echo "=== Athlete Profile ==="
curl -s -H "X-API-Key: $KEY" "$BASE/api/v1/profile" | jq .

echo ""
echo "=== AI Coach Chat ==="
curl -s -X POST -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "What should I focus on this week?"}' \
  "$BASE/api/v1/coach/chat"

echo ""
echo "=== Chat History ==="
curl -s -H "X-API-Key: $KEY" "$BASE/api/v1/coach/history" | jq .
