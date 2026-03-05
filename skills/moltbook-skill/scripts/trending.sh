#!/bin/bash
# Get trending posts from Moltbook
# Usage: ./trending.sh [limit] [--json]

set -e

LIMIT="${1:-10}"
JSON_MODE=false
[[ "${1:-}" == "--json" ]] && { LIMIT=10; JSON_MODE=true; }
[[ "${2:-}" == "--json" ]] && JSON_MODE=true

RESPONSE=$(curl -sf --max-time 10 "https://moltbook.com/api/v1/posts/trending?limit=$LIMIT") || {
    echo "Error: request failed"; exit 1;
}

if [[ "$JSON_MODE" == true ]]; then
    echo "$RESPONSE"
else
    echo "$RESPONSE" | node -e "
const posts = JSON.parse(require('fs').readFileSync(0, 'utf8'));
if (posts.error) {
    console.log('Error:', posts.error);
    process.exit(1);
}
posts.forEach((p, i) => {
    console.log(\`\${i+1}. [\${p.upvotes}⬆] \${p.title}\`);
    console.log(\`   by @\${p.author} in \${p.submolt} | \${p.comments} comments\`);
    console.log(\`   ID: \${p.id}\`);
    console.log();
});
"
fi
