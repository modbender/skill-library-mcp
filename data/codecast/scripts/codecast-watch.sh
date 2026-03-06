#!/bin/bash
# codecast-watch.sh — Poll a PID until it dies, then output the session summary.
# Called by a cron job. The cron job handles posting to the right channel + self-deletion.
# Usage: codecast-watch.sh <PID> <relay-dir>
set -uo pipefail

PID="${1:?Usage: codecast-watch.sh <PID> <relay-dir>}"
RELAY_DIR="${2:?Usage: codecast-watch.sh <PID> <relay-dir>}"

# Check if process is still alive
if kill -0 "$PID" 2>/dev/null; then
  echo "STILL_RUNNING"
  exit 0
fi

# Process is dead — extract results from stream.jsonl
if [[ ! -f "$RELAY_DIR/stream.jsonl" ]]; then
  echo "DONE_NO_DATA"
  exit 0
fi

# Extract result event
python3 -c "
import json, sys
with open('$RELAY_DIR/stream.jsonl') as f:
    for line in f:
        try:
            d = json.loads(line)
            if d.get('type') == 'result':
                turns = d.get('num_turns', '?')
                dur = d.get('duration_ms', 0) // 1000
                cost = d.get('total_cost_usd', 0)
                result = d.get('result', '')[:800]
                status = '✅' if d.get('subtype') == 'success' else '❌'
                print(f'{status} **{turns} turns | {dur}s | \${cost:.2f}**')
                print()
                print(result)
                break
        except:
            pass
    else:
        print('⚠️ Session ended but no result event found in stream.jsonl')
" 2>/dev/null || echo "⚠️ Failed to parse session results"
