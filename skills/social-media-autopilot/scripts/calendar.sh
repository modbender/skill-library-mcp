#!/usr/bin/env bash
# View and manage the content calendar
set -euo pipefail

BASE_DIR="${SOCIAL_MEDIA_DIR:-$HOME/.openclaw/workspace/social-media}"
CALENDAR="$BASE_DIR/calendar.json"

[ ! -f "$CALENDAR" ] && { echo "No calendar found. Run init-workspace.sh first."; exit 1; }

ACTION="${1:---week}"

case $ACTION in
  --week)
    echo "📅 This Week's Schedule"
    echo "======================"
    python3 -c "
import json
from datetime import datetime, timedelta

with open('$CALENDAR') as f:
    cal = json.load(f)

now = datetime.utcnow()
week_end = now + timedelta(days=7)

posts = [p for p in cal['posts'] if p.get('scheduled_at')]
posts.sort(key=lambda p: p['scheduled_at'])

for post in posts:
    try:
        dt = datetime.fromisoformat(post['scheduled_at'].replace('Z', '+00:00'))
        if now.replace(tzinfo=dt.tzinfo) <= dt <= week_end.replace(tzinfo=dt.tzinfo):
            status = '✅' if post['status'] == 'published' else '⏳' if post.get('approved') else '📝'
            print(f'  {status} {dt.strftime(\"%a %b %d %H:%M\")} — {post[\"id\"][:8]}... [{post[\"status\"]}]')
    except:
        pass

if not posts:
    print('  No posts scheduled this week.')
"
    ;;
  --month)
    echo "📅 This Month's Schedule"
    echo "========================"
    python3 -c "
import json
from datetime import datetime, timedelta

with open('$CALENDAR') as f:
    cal = json.load(f)

now = datetime.utcnow()
month_end = now + timedelta(days=30)

posts = [p for p in cal['posts'] if p.get('scheduled_at')]
posts.sort(key=lambda p: p['scheduled_at'])

count = 0
for post in posts:
    try:
        dt = datetime.fromisoformat(post['scheduled_at'].replace('Z', '+00:00'))
        if now.replace(tzinfo=dt.tzinfo) <= dt <= month_end.replace(tzinfo=dt.tzinfo):
            status = '✅' if post['status'] == 'published' else '⏳' if post.get('approved') else '📝'
            print(f'  {status} {dt.strftime(\"%a %b %d %H:%M\")} — {post[\"id\"][:8]}... [{post[\"status\"]}]')
            count += 1
    except:
        pass

print(f'\n  Total: {count} posts scheduled')
"
    ;;
  --gaps)
    echo "🔍 Posting Gaps (next 14 days)"
    echo "==============================="
    python3 -c "
import json
from datetime import datetime, timedelta

with open('$CALENDAR') as f:
    cal = json.load(f)

now = datetime.utcnow()
scheduled_dates = set()

for post in cal['posts']:
    if post.get('scheduled_at'):
        try:
            dt = datetime.fromisoformat(post['scheduled_at'].replace('Z', '+00:00'))
            scheduled_dates.add(dt.strftime('%Y-%m-%d'))
        except:
            pass

for i in range(14):
    day = now + timedelta(days=i)
    day_str = day.strftime('%Y-%m-%d')
    if day_str not in scheduled_dates:
        print(f'  ⚠️  {day.strftime(\"%a %b %d\")} — No posts scheduled')
"
    ;;
  *)
    echo "Usage: calendar.sh [--week|--month|--gaps]"
    ;;
esac
