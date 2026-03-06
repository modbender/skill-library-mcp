#!/usr/bin/env bash
# Log heartbeat uptime to a JSON file
LOG="${UPTIME_LOG:-$HOME/.config/heartbeat-pro/uptime.json}"
mkdir -p "$(dirname "$LOG")"

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
EPOCH=$(date +%s)

if [ ! -f "$LOG" ]; then
  echo '{"heartbeats":[],"total":0}' > "$LOG"
fi

# Append heartbeat (keep last 100)
python3 -c "
import json, sys
with open('$LOG') as f: data = json.load(f)
data['heartbeats'].append({'ts': '$TIMESTAMP', 'epoch': $EPOCH})
data['heartbeats'] = data['heartbeats'][-100:]
data['total'] = data.get('total', 0) + 1
with open('$LOG', 'w') as f: json.dump(data, f)
print(f'💓 Heartbeat #{data[\"total\"]} logged at $TIMESTAMP')
if len(data['heartbeats']) >= 2:
    gap = $EPOCH - data['heartbeats'][-2]['epoch']
    print(f'   Gap since last: {gap//60}m {gap%60}s')
" 2>/dev/null || echo "💓 Heartbeat logged at $TIMESTAMP"
