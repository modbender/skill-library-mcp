#!/bin/bash
# Read a Moltbook post
# Usage: ./read.sh <post_id>

set -e

POST_ID="${1:?Usage: $0 <post_id>}"

curl -s "https://moltbook.com/api/v1/posts/$POST_ID" | \
    node -e "
const post = JSON.parse(require('fs').readFileSync(0, 'utf8'));
if (post.error) {
    console.log('Error:', post.error);
    process.exit(1);
}
console.log('━'.repeat(60));
console.log(\`📝 \${post.title}\`);
console.log(\`👤 @\${post.author} | 🦞 \${post.submolt} | ⬆️ \${post.upvotes}\`);
console.log('━'.repeat(60));
console.log(post.content);
console.log('━'.repeat(60));
if (post.comments?.length) {
    console.log(\`\n💬 Comments (\${post.comments.length}):\`);
    post.comments.forEach(c => {
        console.log(\`  @\${c.author}: \${c.text}\`);
    });
}
" 2>/dev/null || curl -s "https://moltbook.com/api/v1/posts/$POST_ID"
