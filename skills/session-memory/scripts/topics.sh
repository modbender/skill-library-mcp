#!/bin/bash
# List all memory topics
# Usage: ./topics.sh [--json]

MEMORY_DIR="${AGENT_MEMORY_DIR:-$HOME/.agent-memory}"
JSON_MODE=false
[[ "${1:-}" == "--json" ]] && JSON_MODE=true

if [ ! -d "$MEMORY_DIR" ]; then
    echo "No memories found."
    exit 0
fi

# Correct glob depth: YYYY/MM/DD.jsonl
cat "$MEMORY_DIR"/*/*/*.jsonl 2>/dev/null | \
    node -e "
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const topics = {};
const jsonMode = process.argv[1] === 'true';

rl.on('line', line => {
    try {
        const entry = JSON.parse(line);
        topics[entry.topic] = (topics[entry.topic] || 0) + 1;
    } catch (e) {}
});

rl.on('close', () => {
    const sorted = Object.entries(topics).sort((a, b) => b[1] - a[1]);

    if (jsonMode) {
        console.log(JSON.stringify(Object.fromEntries(sorted)));
        return;
    }

    console.log('Memory Topics:\n');
    sorted.forEach(([topic, count]) => {
        console.log(\`  \${topic}: \${count} entries\`);
    });
    console.log(\`\nTotal: \${sorted.reduce((a, b) => a + b[1], 0)} memories\`);
});
" "$JSON_MODE"
