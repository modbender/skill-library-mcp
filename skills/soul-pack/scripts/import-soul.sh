#!/usr/bin/env bash
set -euo pipefail

PKG=""
AGENT=""
WS=""
FORCE="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --package) PKG="$2"; shift 2 ;;
    --agent) AGENT="$2"; shift 2 ;;
    --workspace) WS="$2"; shift 2 ;;
    --force) FORCE="1"; shift 1 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

[[ -n "$PKG" && -n "$AGENT" && -n "$WS" ]] || {
  echo "Usage: import-soul.sh --package <tar.gz|dir> --agent <id> --workspace <path> [--force]"
  exit 1
}

TMP=$(mktemp -d)
cleanup(){ rm -rf "$TMP"; }
trap cleanup EXIT

SRC="$TMP/pkg"
mkdir -p "$SRC"

if [[ -d "$PKG" ]]; then
  cp -R "$PKG"/* "$SRC"/
else
  tar -xzf "$PKG" -C "$SRC" --strip-components=1
fi

[[ -f "$SRC/manifest.json" && -f "$SRC/SOUL.md" ]] || { echo "Invalid package: missing manifest.json or SOUL.md"; exit 1; }

python3 - <<'PY' "$SRC/manifest.json"
import json,sys
p=sys.argv[1]
obj=json.load(open(p))
req=['name','version','createdAt','files']
for k in req:
    assert k in obj, f'missing field: {k}'
files=set(obj.get('files',[]))
for need in ['SOUL.md','preview.md','manifest.json']:
    assert need in files, f'missing in files[]: {need}'
print('manifest: ok')
PY

mkdir -p "$WS"
if [[ -f "$WS/SOUL.md" && "$FORCE" != "1" ]]; then
  echo "Refusing to overwrite existing $WS/SOUL.md (use --force)"
  exit 1
fi

cp "$SRC/SOUL.md" "$WS/SOUL.md"
[[ -f "$SRC/preview.md" ]] && cp "$SRC/preview.md" "$WS/preview.md" || true
cp "$SRC/manifest.json" "$WS/soul-manifest.json"

# Add agent if not exists
if openclaw agents list | grep -q "\b$AGENT\b"; then
  echo "Agent exists: $AGENT"
else
  openclaw agents add "$AGENT" --workspace "$WS"
fi

echo "OK"
echo "AGENT: $AGENT"
echo "WORKSPACE: $WS"