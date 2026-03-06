#!/bin/bash
# Get memories from a specific day
# Usage: ./daily.sh [YYYY-MM-DD] [--json]

DATE="${1:-$(date -u +%Y-%m-%d)}"
JSON_MODE=false
[[ "${1:-}" == "--json" ]] && { DATE=$(date -u +%Y-%m-%d); JSON_MODE=true; }
[[ "${2:-}" == "--json" ]] && JSON_MODE=true

MEMORY_DIR="${AGENT_MEMORY_DIR:-$HOME/.agent-memory}"

YEAR=$(echo "$DATE" | cut -d- -f1)
MONTH=$(echo "$DATE" | cut -d- -f2)
DAY=$(echo "$DATE" | cut -d- -f3)

FILE="$MEMORY_DIR/$YEAR/$MONTH/$DAY.jsonl"

if [ ! -f "$FILE" ]; then
    [[ "$JSON_MODE" == true ]] && echo "[]" || echo "No memories for $DATE"
    exit 0
fi

if [[ "$JSON_MODE" == true ]]; then
    node -e "
const lines = require('fs').readFileSync('$FILE','utf8').trim().split('\n');
const entries = lines.map(l => { try { return JSON.parse(l); } catch(e) { return null; } }).filter(Boolean);
console.log(JSON.stringify(entries));
"
else
    echo "Memories for $DATE:"
    echo
    cat "$FILE" | node -e "
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });

rl.on('line', line => {
    try {
        const m = JSON.parse(line);
        const time = new Date(m.ts).toISOString().split('T')[1].slice(0, 5);
        console.log(\`[\${time}] [\${m.topic}] \${m.content}\`);
        if (m.tags?.length) console.log(\`         tags: \${m.tags.join(', ')}\`);
    } catch (e) {}
});
"
fi
