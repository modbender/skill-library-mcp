#!/usr/bin/env bash
set -euo pipefail

# minimax_web_search.sh
# Wrapper for: mcporter call minimax.web_search query="..."

print_help() {
  cat <<'EOF'
Usage:
  minimax_web_search.sh --query "your query" [options]

Options:
  --query <text>          Search query (required)
  --count <n>             Max items to print (default: 5)
  --freshness <value>     Optional freshness hint (e.g. pd/pw/pm/py or date phrase)
  --json                  Print normalized JSON instead of plain text
  --raw                   Print raw mcporter JSON result
  --preflight             Run environment checks only
  --timeout <seconds>     Max runtime seconds for mcporter call (default: 35)
  --help                  Show this help

Exit codes:
  0 success
  2 invalid arguments
  3 dependency missing (mcporter/python3)
  4 configuration/auth issue
  5 upstream/network/runtime error
  6 no results (non-fatal)
EOF
}

QUERY=""
COUNT=5
FRESHNESS=""
OUT_MODE="text"   # text | json | raw
PREFLIGHT_ONLY=0
TIMEOUT_SECONDS=35

while [[ $# -gt 0 ]]; do
  case "$1" in
    --query)
      QUERY="${2:-}"
      shift 2
      ;;
    --count)
      COUNT="${2:-}"
      shift 2
      ;;
    --freshness)
      FRESHNESS="${2:-}"
      shift 2
      ;;
    --json)
      OUT_MODE="json"
      shift
      ;;
    --raw)
      OUT_MODE="raw"
      shift
      ;;
    --preflight)
      PREFLIGHT_ONLY=1
      shift
      ;;
    --timeout)
      TIMEOUT_SECONDS="${2:-}"
      shift 2
      ;;
    --help|-h)
      print_help
      exit 0
      ;;
    *)
      echo "[ERR] Unknown argument: $1" >&2
      print_help >&2
      exit 2
      ;;
  esac
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERR] python3 is required" >&2
  exit 3
fi

if ! command -v mcporter >/dev/null 2>&1; then
  echo "[ERR] mcporter not found. Install/configure mcporter first." >&2
  exit 3
fi

if ! [[ "$COUNT" =~ ^[0-9]+$ ]] || [[ "$COUNT" -lt 1 ]]; then
  echo "[ERR] --count must be a positive integer" >&2
  exit 2
fi

if ! [[ "$TIMEOUT_SECONDS" =~ ^[0-9]+$ ]] || [[ "$TIMEOUT_SECONDS" -lt 1 ]]; then
  echo "[ERR] --timeout must be a positive integer" >&2
  exit 2
fi

LIST_ERR=$(mktemp)
TMP_OUT=$(mktemp)
TMP_ERR=$(mktemp)
trap 'rm -f "$LIST_ERR" "$TMP_OUT" "$TMP_ERR"' EXIT

# Preflight: verify minimax server is visible in mcporter list
if ! LIST_JSON=$(mcporter list --json 2>"$LIST_ERR"); then
  echo "[ERR] Failed to run 'mcporter list --json'" >&2
  sed -n '1,80p' "$LIST_ERR" >&2 || true
  exit 4
fi

if ! python3 - "$LIST_JSON" <<'PY'
import json, sys
raw = sys.argv[1]
obj = json.loads(raw)
servers = obj.get("servers", [])
ok = any(s.get("name") == "minimax" and s.get("status") == "ok" for s in servers)
if not ok:
    print("[ERR] minimax MCP server not ready. Check config/mcporter.json and API key.", file=sys.stderr)
    sys.exit(1)
PY
then
  exit 4
fi

if [[ "$PREFLIGHT_ONLY" -eq 1 ]]; then
  echo "[OK] Preflight passed: mcporter + minimax MCP are available."
  exit 0
fi

if [[ -z "$QUERY" ]]; then
  echo "[ERR] --query is required (unless using --preflight)" >&2
  exit 2
fi

# minimax.web_search currently requires only query; freshness is appended into query hint.
QUERY_EFF="$QUERY"
if [[ -n "$FRESHNESS" ]]; then
  QUERY_EFF="$QUERY (freshness: $FRESHNESS)"
fi

if ! timeout "$TIMEOUT_SECONDS" mcporter call minimax.web_search query="$QUERY_EFF" >"$TMP_OUT" 2>"$TMP_ERR"; then
  echo "[ERR] web_search call failed" >&2
  sed -n '1,80p' "$TMP_ERR" >&2 || true
  if grep -Eiq 'auth|apikey|api key|unauthorized|forbidden|401|403' "$TMP_ERR"; then
    exit 4
  fi
  exit 5
fi

if [[ "$OUT_MODE" == "raw" ]]; then
  cat "$TMP_OUT"
  exit 0
fi

if [[ "$OUT_MODE" == "json" ]]; then
  python3 - "$TMP_OUT" "$COUNT" <<'PY'
import json, sys
path, count = sys.argv[1], int(sys.argv[2])
raw = open(path, 'r', encoding='utf-8').read()
obj = json.loads(raw)
organic = obj.get('organic') or []
out = {
  'query': obj.get('query'),
  'count': min(count, len(organic)),
  'results': [
    {
      'title': r.get('title', '').strip(),
      'url': r.get('link', '').strip(),
      'snippet': (r.get('snippet', '') or '').strip(),
      'date': (r.get('date', '') or '').strip(),
    }
    for r in organic[:count]
  ],
  'related_searches': [x.get('query') for x in (obj.get('related_searches') or []) if x.get('query')],
}
print(json.dumps(out, ensure_ascii=False, indent=2))
PY
  if [[ $(python3 - "$TMP_OUT" <<'PY'
import json,sys
o=json.loads(open(sys.argv[1],encoding='utf-8').read())
print(len(o.get('organic') or []))
PY
) -eq 0 ]]; then
    exit 6
  fi
  exit 0
fi

# text mode
python3 - "$TMP_OUT" "$COUNT" <<'PY'
import json, sys
path, count = sys.argv[1], int(sys.argv[2])
obj = json.loads(open(path, 'r', encoding='utf-8').read())
organic = obj.get('organic') or []
if not organic:
    print("No results.")
    sys.exit(6)
print("Top results:")
for i, r in enumerate(organic[:count], 1):
    t = (r.get('title') or '').strip() or '(no title)'
    u = (r.get('link') or '').strip()
    s = (r.get('snippet') or '').strip()
    d = (r.get('date') or '').strip()
    print(f"{i}. {t}")
    if d:
      print(f"   Date: {d}")
    if u:
      print(f"   URL: {u}")
    if s:
      print(f"   Snippet: {s}")
PY
rc=$?
if [[ $rc -eq 6 ]]; then
  exit 6
fi
exit 0
