#!/bin/bash
# NOFX AI500 New Coin Monitor
# Compares API coin list against local known list
# Output: NEW:<json> | REMOVED:<coins> | NO_CHANGE

KEY="${NOFX_KEY:-cm_568c67eae410d912c54c}"
BASE="${NOFX_BASE:-https://nofxos.ai}"
KNOWN_FILE="${NOFX_KNOWN_FILE:-$HOME/.openclaw/workspace/nofx-ai500-known.json}"

RESPONSE=$(curl -s "${BASE}/api/ai500/list?auth=${KEY}")

CURRENT=$(echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('success'):
    for c in d['data']['coins']:
        print(c['pair'])
")

if [ -f "$KNOWN_FILE" ]; then
    KNOWN=$(python3 -c "import json; print('\n'.join(json.load(open('$KNOWN_FILE'))))")
else
    KNOWN=""
fi

NEW_COINS=""
for coin in $CURRENT; do
    if ! echo "$KNOWN" | grep -q "^${coin}$"; then
        NEW_COINS="${NEW_COINS} ${coin}"
    fi
done

if [ -n "$NEW_COINS" ]; then
    NEW_JSON=$(echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
try:
    known = set(json.load(open('$KNOWN_FILE')))
except:
    known = set()
new_coins = [c for c in d['data']['coins'] if c['pair'] not in known]
json.dump(new_coins, sys.stdout, indent=2)
")
    # Update known list
    echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
pairs = [c['pair'] for c in d['data']['coins']]
try:
    old = json.load(open('$KNOWN_FILE'))
except:
    old = []
json.dump(list(set(old + pairs)), open('$KNOWN_FILE', 'w'))
"
    echo "NEW:${NEW_JSON}"
else
    REMOVED=""
    for coin in $KNOWN; do
        [ -n "$coin" ] && ! echo "$CURRENT" | grep -q "^${coin}$" && REMOVED="${REMOVED} ${coin}"
    done
    if [ -n "$REMOVED" ]; then
        echo "REMOVED:${REMOVED}"
        echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
json.dump([c['pair'] for c in d['data']['coins']], open('$KNOWN_FILE', 'w'))
"
    else
        echo "NO_CHANGE"
    fi
fi
