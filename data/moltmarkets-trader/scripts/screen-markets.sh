#!/usr/bin/env bash
# Screen open MoltMarkets markets for trading opportunities
set -euo pipefail

API_BASE="https://api.zcombinator.io/molt"
MM_KEY=$(cat ~/secrets/moltmarkets-api-key)

# Fetch all markets
MARKETS=$(curl -s -H "Authorization: Bearer $MM_KEY" "$API_BASE/markets")

if [ -z "$MARKETS" ] || [ "$MARKETS" = "[]" ]; then
  echo "No markets found."
  exit 0
fi

# Current time as epoch
NOW=$(date +%s)

echo "═══════════════════════════════════════════════════════════════"
echo "  MOLTMARKETS OPEN MARKET SCANNER"
echo "  $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Parse and display open markets
echo "$MARKETS" | python3 -c "
import json, sys
from datetime import datetime, timezone

markets = json.load(sys.stdin)
now = datetime.now(timezone.utc)
open_markets = [m for m in markets if m.get('status') == 'OPEN']

if not open_markets:
    print('No open markets found.')
    sys.exit(0)

print(f'Found {len(open_markets)} open market(s):')
print()

for m in open_markets:
    mid = m['id'][:8]
    title = m['title']
    prob = m.get('probability', 0.5)
    vol = m.get('total_volume', 0)
    closes_at = m.get('closes_at', '')
    creator = m.get('creator_username', '?')
    
    # Calculate time remaining
    try:
        close_dt = datetime.fromisoformat(closes_at.replace('Z', '+00:00'))
        delta = close_dt - now
        if delta.total_seconds() <= 0:
            time_left = 'EXPIRED'
        elif delta.days > 0:
            time_left = f'{delta.days}d {delta.seconds // 3600}h'
        elif delta.seconds >= 3600:
            time_left = f'{delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m'
        else:
            time_left = f'{delta.seconds // 60}m'
    except:
        time_left = '?'
    
    # Flag opportunities
    flags = []
    if prob > 0.90:
        flags.append('⚡ HIGH PROB (>90%)')
    elif prob < 0.10:
        flags.append('⚡ LOW PROB (<10%)')
    if vol < 20:
        flags.append('📉 LOW VOLUME')
    if time_left not in ('?', 'EXPIRED') and 'h' not in time_left and 'd' not in time_left:
        flags.append('⏰ CLOSING SOON')
    
    print(f'┌─ {title}')
    print(f'│  ID: {m[\"id\"]}')
    print(f'│  Prob: {prob:.1%}  │  Volume: {vol:.0f}ŧ  │  Closes: {time_left}')
    print(f'│  Creator: {creator}  │  Close time: {closes_at}')
    if flags:
        print(f'│  🚩 {\" | \".join(flags)}')
    print(f'└───────────────────────────────────────────')
    print()

# Summary
total_vol = sum(m.get('total_volume', 0) for m in open_markets)
flagged = sum(1 for m in open_markets if m.get('probability', 0.5) > 0.9 or m.get('probability', 0.5) < 0.1)
print(f'Summary: {len(open_markets)} open | {total_vol:.0f}ŧ total volume | {flagged} flagged')
"
