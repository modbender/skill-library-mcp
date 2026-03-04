#!/bin/bash
# Get trending posts from Moltbook

set -e

LIMIT="${1:-10}"

curl -s "https://moltbook.com/api/v1/posts/trending?limit=$LIMIT" | \
    node -e "
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
" 2>/dev/null || echo "Install Node.js for formatted output, or use raw JSON"
