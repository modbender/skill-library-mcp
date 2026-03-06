#!/bin/bash
# Search memories
# Usage: ./recall.sh "search query" [--json]

set -e

QUERY="${1:?Usage: $0 \"search query\" [--json]}"
JSON_MODE=false
[[ "${2:-}" == "--json" ]] && JSON_MODE=true

MEMORY_DIR="${AGENT_MEMORY_DIR:-$HOME/.agent-memory}"

if [ ! -d "$MEMORY_DIR" ]; then
    echo "No memories found. Start saving with ./save.sh"
    exit 0
fi

# Search through all jsonl files (correct depth: YYYY/MM/DD.jsonl)
grep -r -i -h "$QUERY" "$MEMORY_DIR"/*/*/*.jsonl 2>/dev/null | \
    node -e "
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const results = [];
const jsonMode = process.argv[1] === 'true';

rl.on('line', line => {
    try {
        const entry = JSON.parse(line);
        // Also verify the query actually matches topic or content (not just any field)
        const q = process.argv[2].toLowerCase();
        if (entry.content.toLowerCase().includes(q) || entry.topic.toLowerCase().includes(q) ||
            (entry.tags || []).some(t => t.toLowerCase().includes(q))) {
            results.push(entry);
        }
    } catch (e) {}
});

rl.on('close', () => {
    results.sort((a, b) => b.ts - a.ts);

    if (jsonMode) {
        console.log(JSON.stringify(results.slice(0, 20)));
        return;
    }

    if (results.length === 0) {
        console.log('No memories found for: ' + process.argv[2]);
        return;
    }

    console.log(\`Found \${results.length} memories:\n\`);
    results.slice(0, 10).forEach(m => {
        const date = new Date(m.ts).toISOString().split('T')[0];
        console.log(\`[\${date}] [\${m.topic}] \${m.content}\`);
        if (m.tags?.length) console.log(\`         tags: \${m.tags.join(', ')}\`);
        console.log();
    });

    if (results.length > 10) {
        console.log(\`... and \${results.length - 10} more\`);
    }
});
" "$JSON_MODE" "$QUERY"
