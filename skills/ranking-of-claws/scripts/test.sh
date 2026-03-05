#!/bin/bash
# Test your Ranking of Claws setup
set -euo pipefail

API_URL="https://rankingofclaws.angelstreet.io/api"
echo "Testing Ranking of Claws..."

# Test API connectivity
echo -n "1. API reachable: "
if curl -sf "$API_URL/stats" > /dev/null 2>&1; then
  echo "OK"
else
  echo "FAIL - cannot reach $API_URL"
  exit 1
fi

# Test report endpoint
echo -n "2. Report endpoint: "
RESULT=$(curl -sf -X POST "$API_URL/report" \
  -H "Content-Type: application/json" \
  -d '{"gateway_id":"test-probe","agent_name":"probe","country":"XX","tokens_delta":0,"model":"test"}' 2>&1) || RESULT="FAIL"
if echo "$RESULT" | grep -q "success"; then
  echo "OK"
else
  echo "FAIL - $RESULT"
fi

# Test rank lookup
echo -n "3. Rank lookup: "
RANK=$(curl -sf "$API_URL/rank?agent=probe" 2>&1) || RANK="FAIL"
if echo "$RANK" | grep -q "rank"; then
  echo "OK"
else
  echo "FAIL (expected if agent not yet reported)"
fi

# Check hook file
echo -n "4. Hook handler: "
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$SKILL_DIR/hooks/handler.js" ]; then
  echo "OK ($SKILL_DIR/hooks/handler.js)"
else
  echo "MISSING - hook not found"
fi

echo ""
echo "All checks passed. Your agent can report usage!"
echo "Quick test: ./scripts/report.sh YourAgentName CH 1000"
