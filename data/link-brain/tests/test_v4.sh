#!/usr/bin/env bash
set -euo pipefail

export LINK_BRAIN_DIR=/tmp/test-link-brain-v4

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRAIN="$ROOT_DIR/scripts/brain.py"

rm -rf "$LINK_BRAIN_DIR"
mkdir -p "$LINK_BRAIN_DIR"

python3 "$BRAIN" setup >/dev/null

# Create a local HTML page so auto-save can fetch without relying on the network.
HTML_PATH="$LINK_BRAIN_DIR/sample.html"
cat >"$HTML_PATH" <<'HTML'
<!doctype html>
<html>
<head>
  <title>SQLite FTS5 tips and tricks</title>
</head>
<body>
<h1>SQLite full-text search</h1>
<p>FTS5 is fast for search across notes and bookmarks.</p>
<p>This page explains tokenizers, prefix queries, and ranking.</p>
<p>It also mentions spaced repetition and review queues.</p>
</body>
</html>
HTML

FILE_URL="file://$HTML_PATH"

json_get() {
  local expr="$1"
  python3 -c "import json,sys; obj=json.load(sys.stdin); print(${expr})"
}

# 1) Auto-save via `save --auto`
OUT_AUTO_SAVE="$(python3 "$BRAIN" save "$FILE_URL" --auto)"
printf '%s' "$OUT_AUTO_SAVE" | python3 -c "import json,sys; obj=json.load(sys.stdin); \
assert obj['status']=='saved'; \
assert obj.get('auto') is True; \
link=obj['link']; \
assert link['url'].startswith('file://'); \
assert 'sqlite' in (link.get('title') or '').lower(); \
assert isinstance(link.get('tags'), list) and len(link['tags'])>=1; \
assert isinstance(link.get('summary',''), str) and len(link.get('summary',''))>10; \
print('ok: auto-save')"

LINK_ID="$(printf '%s' "$OUT_AUTO_SAVE" | json_get "obj['link']['id']")"

# 2) Manual save with known domain and content
OUT_MANUAL="$(python3 "$BRAIN" save "https://github.com/sqlite/sqlite" --title "SQLite source" --summary "Mirror repo." --tags "sqlite, repo")"
printf '%s' "$OUT_MANUAL" | python3 -c "import json,sys; obj=json.load(sys.stdin); \
assert obj['status']=='saved'; \
assert obj['link']['url'].startswith('https://github.com/'); \
print('ok: manual save')"

LINK_ID_2="$(printf '%s' "$OUT_MANUAL" | json_get "obj['link']['id']")"

# Make link #2 older so time parsing can exclude it.
python3 -c "import sqlite3, os; from datetime import datetime, timezone, timedelta; from pathlib import Path; \
DB=Path(os.environ['LINK_BRAIN_DIR'])/'brain.db'; \
db=sqlite3.connect(str(DB)); \
old=(datetime.now(timezone.utc)-timedelta(days=400)).isoformat(); \
db.execute('UPDATE links SET saved_at=?, updated_at=? WHERE id=?',(old,old,int('$LINK_ID_2'))); \
db.commit(); \
print('ok: time adjust')"

# 3) Status and rating filters
python3 "$BRAIN" rate "$LINK_ID" 5 >/dev/null
python3 "$BRAIN" read "$LINK_ID" >/dev/null

OUT_Q1="$(python3 "$BRAIN" search "last 7 days" --limit 50)"
printf '%s' "$OUT_Q1" | python3 -c "import json,sys; obj=json.load(sys.stdin); \
assert isinstance(obj, list); \
ids=[x['id'] for x in obj]; \
assert int('$LINK_ID') in ids; \
assert int('$LINK_ID_2') not in ids; \
print('ok: time filter')"

OUT_Q1B="$(python3 "$BRAIN" search "from github" --limit 50)"
printf '%s' "$OUT_Q1B" | python3 -c "import json,sys; obj=json.load(sys.stdin); \
assert isinstance(obj, list); \
ids=[x['id'] for x in obj]; \
assert int('$LINK_ID_2') in ids; \
print('ok: source filter')"

OUT_Q2="$(python3 "$BRAIN" search "best rated read sqlite" --limit 10)"
printf '%s' "$OUT_Q2" | python3 -c "import json,sys; obj=json.load(sys.stdin); \
assert isinstance(obj, list); \
assert any(x['id']==int('$LINK_ID') for x in obj); \
print('ok: status + rating + sort')"

# 4) Collections
python3 "$BRAIN" collection create "Test List" --description "A small list" >/dev/null
python3 "$BRAIN" collection add "Test List" "$LINK_ID" >/dev/null
python3 "$BRAIN" collection add "Test List" "$LINK_ID_2" >/dev/null

OUT_SHOW="$(python3 "$BRAIN" collection show "Test List")"
printf '%s' "$OUT_SHOW" | python3 -c "import json,sys; obj=json.load(sys.stdin); \
assert obj['collection']['name']=='Test List'; \
assert obj['count']==2; \
print('ok: collections show')"

OUT_EXPORT_MD="$(python3 "$BRAIN" collection export "Test List")"
MD_PATH="$(printf '%s' "$OUT_EXPORT_MD" | json_get "obj['path']")"
[ -f "$MD_PATH" ]
echo "ok: export md"

OUT_EXPORT_HTML="$(python3 "$BRAIN" collection export "Test List" --html)"
HTML_OUT_PATH="$(printf '%s' "$OUT_EXPORT_HTML" | json_get "obj['path']")"
[ -f "$HTML_OUT_PATH" ]
echo "ok: export html"

# 5) Review queue
OUT_NEXT="$(python3 "$BRAIN" review next)"
printf '%s' "$OUT_NEXT" | python3 -c "import json,sys; obj=json.load(sys.stdin); \
assert obj['status'] in ('ok','empty'); \
print('ok: review next')"

# 6) Graph output
OUT_GRAPH="$(python3 "$BRAIN" graph)"
GRAPH_PATH="$(printf '%s' "$OUT_GRAPH" | json_get "obj['path']")"
[ -f "$GRAPH_PATH" ]
echo "ok: graph"

echo "ALL_V4_TESTS_OK"