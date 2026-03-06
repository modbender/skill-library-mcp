#!/usr/bin/env bash
# ask-council.sh — Quick headless access to LLM Council
# Usage: ask-council.sh "Your question here"
#
# Returns: Chairman's synthesized answer (or error message)

set -euo pipefail

API_BASE="http://127.0.0.1:8001"
TIMEOUT_SEC=120

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
error() { echo -e "${RED}[council-brief]${NC} $*" >&2; exit 1; }
info()  { echo -e "${GREEN}[council-brief]${NC} $*"; }
warn()  { echo -e "${YELLOW}[council-brief]${NC} $*"; }

# ── Check input ───────────────────────────────────────────────────────────────
QUESTION="${1:-}"
if [[ -z "$QUESTION" ]]; then
  error "Usage: ask-council.sh 'Your question here'"
fi

# ── Check if backend is running ───────────────────────────────────────────────
if ! curl -s "$API_BASE/" > /dev/null 2>&1; then
  error "LLM Council backend not running. Start it first:\n  /council-brief install"
fi

# ── Create conversation ───────────────────────────────────────────────────────
CONVO_RESPONSE=$(curl -s -X POST "$API_BASE/api/conversations" -H "Content-Type: application/json" -d '{}')
CONVO_ID=$(echo "$CONVO_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
SHORT_ID=$(echo "$CONVO_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('short_id', ''))")
if [[ -z "$CONVO_ID" ]]; then
  error "Failed to create conversation"
fi

# ── Start council run ─────────────────────────────────────────────────────────
RUN_RESPONSE=$(curl -s -X POST "$API_BASE/api/conversations/$CONVO_ID/runs" \
  -H "Content-Type: application/json" \
  -d "{\"content\": $(echo "$QUESTION" | python3 -c 'import json, sys; print(json.dumps(sys.stdin.read().strip()))')}")
RUN_ID=$(echo "$RUN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['run_id'])")
if [[ -z "$RUN_ID" ]]; then
  error "Failed to start council run"
fi

info "Council is deliberating... (this may take 30-60s)"

# ── Poll until complete ───────────────────────────────────────────────────────
START_TIME=$(date +%s)
while true; do
  NOW=$(date +%s)
  ELAPSED=$((NOW - START_TIME))
  
  if [[ $ELAPSED -gt $TIMEOUT_SEC ]]; then
    error "Timed out after ${TIMEOUT_SEC}s. The council is still talking."
  fi

  STATUS=$(curl -s "$API_BASE/api/conversations/$CONVO_ID/runs/$RUN_ID")
  RUN_STATE=$(echo "$STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")
  
  case "$RUN_STATE" in
    complete)
      break
      ;;
    failed|canceled)
      ERROR=$(echo "$STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown error'))")
      error "Council session failed: $ERROR"
      ;;
    *)
      sleep 2
      echo -n "."
      ;;
  esac
done

echo ""  # newline after dots

# ── Extract chairman answer ───────────────────────────────────────────────────
CHAIRMAN_ANSWER=$(echo "$STATUS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
stage3 = data.get('stage3', {})
if stage3.get('status') == 'complete':
    result = stage3.get('data', {})
    print(result.get('response', 'No answer found'))
else:
    print('Chairman did not complete synthesis')")

# ── Output ────────────────────────────────────────────────────────────────────
LOCAL_IP="$(hostname -I | awk '{print $1}')"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "                    CHAIRMAN'S ANSWER"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "$CHAIRMAN_ANSWER"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
if [[ -n "$SHORT_ID" ]]; then
  echo "Short ID: $SHORT_ID"
  echo ""
  echo "View full discussion: http://${LOCAL_IP}:5173/c/${SHORT_ID}"
else
  echo "Conversation ID: $CONVO_ID"
  echo ""
  echo "View full discussion: http://${LOCAL_IP}:5173"
fi
echo ""
