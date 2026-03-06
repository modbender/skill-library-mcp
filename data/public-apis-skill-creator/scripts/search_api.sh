#!/usr/bin/env bash
# Usage:
#   search_api.sh "weather"
#   search_api.sh "weather" --top 5 --json

set -euo pipefail

CACHE_DIR="${HOME}/.cache/public-apis-helper"
CACHE_FILE="${CACHE_DIR}/apis.json"
CACHE_TTL=86400
TOP=10
JSON_OUT=0

QUERY="${1:-}"
shift || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --top) TOP="$2"; shift 2 ;;
    --json) JSON_OUT=1; shift ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

if [[ -z "$QUERY" ]]; then
  echo "Usage: search_api.sh <query> [--top N] [--json]"
  exit 1
fi

mkdir -p "$CACHE_DIR"

update_cache() {
  echo "[INFO] 正在更新 API 列表缓存..." >&2
  curl -s "https://api.github.com/repos/public-apis/public-apis/contents/README.md" | \
    python3 - "$CACHE_FILE" <<'PY'
import sys, json, base64, re
out = sys.argv[1]
data = json.load(sys.stdin)
content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')

apis = []
category = ''
for raw in content.splitlines():
    line = raw.strip()
    if line.startswith('### '):
        category = line[4:].strip()
        continue
    if not line.startswith('|') or '---' in line or 'API' in line and 'Description' in line:
        continue

    parts = [p.strip() for p in line.split('|')[1:-1]]
    if len(parts) < 6:
        continue

    def md_link_text(s):
        m = re.search(r'\[(.*?)\]\((.*?)\)', s)
        if m:
            return m.group(1), m.group(2)
        return s, ''

    name, link = md_link_text(parts[0])
    apis.append({
        'name': name,
        'description': parts[1],
        'auth': parts[2],
        'https': parts[3],
        'cors': parts[4],
        'link': link,
        'category': category,
    })

with open(out, 'w', encoding='utf-8') as f:
    json.dump(apis, f, ensure_ascii=False, indent=2)
print(f"[INFO] 缓存更新完成，共 {len(apis)} 条", file=sys.stderr)
PY
}

if [[ ! -f "$CACHE_FILE" ]] || [[ $(( $(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0) )) -gt $CACHE_TTL ]]; then
  update_cache
fi

python3 - "$CACHE_FILE" "$QUERY" "$TOP" "$JSON_OUT" <<'PY'
import json, sys, re
cache, query, top, json_out = sys.argv[1], sys.argv[2].lower(), int(sys.argv[3]), int(sys.argv[4])
with open(cache, 'r', encoding='utf-8') as f:
    apis = json.load(f)

# 归一化 markdown 链接格式: [Name](url)
for a in apis:
    m = re.search(r'\[(.*?)\]\((.*?)\)', a.get('name',''))
    if m:
        a['name'] = m.group(1)
        if not a.get('link'):
            a['link'] = m.group(2)

q_words = [w for w in re.split(r'\W+', query) if w]

def score(api):
    s = 0
    name = api['name'].lower()
    desc = api['description'].lower()
    cat = api['category'].lower()
    full = f"{name} {desc} {cat}"
    if query in name: s += 12
    if query in desc: s += 8
    if query in cat: s += 6
    for w in q_words:
        if len(w) < 2: continue
        if w in name: s += 4
        if w in desc: s += 3
        if w in cat: s += 2
        if w in full: s += 1
    if api.get('auth','').lower() in ('no','null','none',''): s += 1
    if api.get('https','').lower() == 'yes': s += 1
    return s

for a in apis:
    a['score'] = score(a)

results = [a for a in apis if a['score'] > 0]
results.sort(key=lambda x: x['score'], reverse=True)
results = results[:top]

if json_out:
    print(json.dumps(results, ensure_ascii=False, indent=2))
    sys.exit(0)

if not results:
    print('❌ 未找到匹配的 API')
    sys.exit(1)

print(f"🔍 搜索: {query}\n")
print(f"✅ 找到 {len(results)} 个相关 API:\n")
for i, api in enumerate(results, 1):
    print(f"{i}. {api['name']}")
    print(f"   📋 {api['description']}")
    print(f"   📁 分类: {api['category']}")
    print(f"   🔐 认证: {api['auth'] or 'No'}")
    print(f"   🔒 HTTPS: {api['https']}")
    print(f"   🌐 CORS: {api['cors']}")
    if api.get('link'): print(f"   🔗 文档: {api['link']}")
    print()
PY