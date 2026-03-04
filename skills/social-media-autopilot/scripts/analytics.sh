#!/usr/bin/env bash
# Pull and display social media analytics
set -euo pipefail

BASE_DIR="${SOCIAL_MEDIA_DIR:-$HOME/.openclaw/workspace/social-media}"
PUBLISHED_DIR="$BASE_DIR/published"
ANALYTICS_DIR="$BASE_DIR/analytics"

ACTION="${1:---last}"
PARAM="${2:-7d}"

case $ACTION in
  --last)
    echo "📊 Analytics — Last $PARAM"
    echo "=========================="
    python3 -c "
import json, os, glob
from datetime import datetime, timedelta

period = '$PARAM'
days = int(period.replace('d', ''))
cutoff = datetime.utcnow() - timedelta(days=days)

published = glob.glob('$PUBLISHED_DIR/*.json')
total_posts = 0
platforms = {}

for f in published:
    with open(f) as fh:
        post = json.load(fh)
    pub_at = post.get('published_at', '')
    if pub_at:
        try:
            dt = datetime.fromisoformat(pub_at.replace('Z', '+00:00'))
            if dt.replace(tzinfo=None) >= cutoff:
                total_posts += 1
                for p in post.get('platforms', []):
                    platforms[p] = platforms.get(p, 0) + 1
        except:
            pass

print(f'  Posts published: {total_posts}')
for p, c in sorted(platforms.items()):
    print(f'    {p}: {c}')

if total_posts == 0:
    print('  No posts found in this period.')
    print('  Tip: Analytics data enriches after posts are published and APIs are connected.')
"
    ;;
  --post)
    POST_ID="$PARAM"
    PUBLISHED_FILE="$PUBLISHED_DIR/$POST_ID.json"
    if [ -f "$PUBLISHED_FILE" ]; then
      echo "📊 Post Analytics: $POST_ID"
      python3 -c "
import json
with open('$PUBLISHED_FILE') as f:
    post = json.load(f)
print(f'  Status: {post[\"status\"]}')
print(f'  Platforms: {\", \".join(post[\"platforms\"])}')
print(f'  Published: {post.get(\"published_at\", \"N/A\")}')
print(f'  Text: {post[\"text\"][:120]}')
# Analytics would be fetched from platform APIs here
print('  ℹ️  Detailed metrics require platform API connections.')
"
    else
      echo "❌ Published post not found: $POST_ID"
    fi
    ;;
  --report)
    echo "📊 Generating $PARAM report..."
    REPORT_FILE="$ANALYTICS_DIR/report-$(date +%Y-%m-%d).md"
    python3 -c "
import json, glob, os
from datetime import datetime, timedelta

published = glob.glob('$PUBLISHED_DIR/*.json')
cutoff = datetime.utcnow() - timedelta(days=7)
posts = []

for f in published:
    with open(f) as fh:
        post = json.load(fh)
    pub_at = post.get('published_at', '')
    if pub_at:
        try:
            dt = datetime.fromisoformat(pub_at.replace('Z', '+00:00'))
            if dt.replace(tzinfo=None) >= cutoff:
                posts.append(post)
        except:
            pass

report = f'# Social Media Report — {datetime.utcnow().strftime(\"%Y-%m-%d\")}\n\n'
report += f'## Summary\n- Posts published: {len(posts)}\n'

platforms = {}
for p in posts:
    for plat in p.get('platforms', []):
        platforms[plat] = platforms.get(plat, 0) + 1

for plat, count in sorted(platforms.items()):
    report += f'- {plat}: {count} posts\n'

report += '\n## Posts\n'
for p in posts:
    report += f'- **{p[\"id\"][:8]}** ({p.get(\"published_at\", \"?\")}) — {\", \".join(p[\"platforms\"])}\n'
    report += f'  > {p[\"text\"][:100]}\n\n'

with open('$REPORT_FILE', 'w') as f:
    f.write(report)

print(f'  ✅ Report saved: $REPORT_FILE')
"
    ;;
  *)
    echo "Usage: analytics.sh [--last <Nd>|--post <post-id>|--report weekly]"
    ;;
esac
