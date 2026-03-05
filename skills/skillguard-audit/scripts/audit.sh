#!/bin/bash
# Quick audit script — calls SkillGuard API
# Usage: audit.sh <skill-name> <code-string>
#   or:  audit.sh <skill-name> --file <path-to-code>

SKILL_NAME="${1:-unknown}"
SKILLGUARD_URL="https://studio-designed-normal-atomic.trycloudflare.com"

if [ "$2" = "--file" ] && [ -n "$3" ]; then
  CODE=$(cat "$3")
else
  CODE="$2"
fi

if [ -z "$CODE" ]; then
  echo "Usage: audit.sh <skill-name> <code-or-'--file path'>"
  exit 1
fi

# Try the API (will get 402 if no payment, but credit endpoint is free with IOU)
RESPONSE=$(curl -s -X POST "$SKILLGUARD_URL/api/audit" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "import json,sys; print(json.dumps({'name': sys.argv[1], 'code': sys.argv[2]}))" "$SKILL_NAME" "$CODE")" 2>/dev/null)

# Check if it's a 402 (payment required)
if echo "$RESPONSE" | grep -q "x402Version"; then
  echo "⚠️  Payment required. Use x402 pay or the credit system."
  echo "   Credit: GET $SKILLGUARD_URL/api/credit/template?address=YOUR_WALLET"
  exit 2
fi

# Parse and display result
echo "$RESPONSE" | python3 -c "
import sys,json
try:
  d = json.load(sys.stdin)
  v = d.get('verdict','?')
  s = d.get('riskScore',0)
  icons = {'SAFE':'✅','LOW_RISK':'🟢','CAUTION':'⚠️','DANGEROUS':'🔴'}
  print(f'{icons.get(v,\"?\")} {v} (risk: {s}/100)')
  for t in d.get('threats',[]):
    print(f'  [{t[\"severity\"]}] {t[\"description\"]}')
except: print(sys.stdin.read())
" 2>/dev/null

exit 0
