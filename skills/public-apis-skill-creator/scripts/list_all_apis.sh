#!/usr/bin/env bash
# 打印 public-apis 全量列表（可选导出 JSON）
# Usage:
#   list_all_apis.sh
#   list_all_apis.sh --json
#   list_all_apis.sh --top 50

set -euo pipefail

CACHE_DIR="${HOME}/.cache/public-apis-helper"
CACHE_FILE="${CACHE_DIR}/apis.json"
CACHE_TTL=86400
TOP=0
JSON_OUT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --top) TOP="$2"; shift 2 ;;
    --json) JSON_OUT=1; shift ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

mkdir -p "$CACHE_DIR"

update_cache() {
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
    if not line.startswith('|') or '---' in line or ('API' in line and 'Description' in line):
        continue
    parts = [p.strip() for p in line.split('|')[1:-1]]
    if len(parts) < 6:
        continue
    m = re.search(r'\[(.*?)\]\((.*?)\)', parts[0])
    if m:
        name, link = m.group(1), m.group(2)
    else:
        name, link = parts[0], ''
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
PY
}

if [[ ! -f "$CACHE_FILE" ]] || [[ $(( $(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0) )) -gt $CACHE_TTL ]]; then
  update_cache
fi

python3 - "$CACHE_FILE" "$TOP" "$JSON_OUT" <<'PY'
import sys, json
cache, top, json_out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
with open(cache, 'r', encoding='utf-8') as f:
    apis = json.load(f)

if top > 0:
    apis = apis[:top]

if json_out:
    print(json.dumps(apis, ensure_ascii=False, indent=2))
    raise SystemExit(0)

print(f"📚 public-apis 总数: {len(apis)}\n")
for i, a in enumerate(apis, 1):
    print(f"{i}. {a['name']}")
    print(f"   📁 {a['category']} | 🔐 {a['auth']} | 🔒 HTTPS:{a['https']} | 🌐 CORS:{a['cors']}")
    if a.get('link'):
        print(f"   🔗 {a['link']}")
PY