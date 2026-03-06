#!/usr/bin/env bash
set -euo pipefail

WS=""
OUT=""
NAME="soul-$(date +%Y%m%d-%H%M%S)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace) WS="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

[[ -n "$WS" && -n "$OUT" ]] || { echo "Usage: export-soul.sh --workspace <path> --out <dir> [--name <pkg>]"; exit 1; }
[[ -f "$WS/SOUL.md" ]] || { echo "SOUL.md not found in workspace: $WS"; exit 1; }

PKG_DIR="$OUT/$NAME"
mkdir -p "$PKG_DIR"
cp "$WS/SOUL.md" "$PKG_DIR/SOUL.md"

cat > "$PKG_DIR/preview.md" <<EOF
# ${NAME}
- Exported from: ${WS}
- Persona source: SOUL.md
EOF

cat > "$PKG_DIR/manifest.json" <<EOF
{
  "name": "${NAME}",
  "version": "0.1.0",
  "description": "Soul package exported from OpenClaw workspace",
  "createdAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "sourceWorkspace": "${WS}",
  "files": ["SOUL.md", "preview.md", "manifest.json"]
}
EOF

( cd "$OUT" && tar -czf "${NAME}.tar.gz" "$NAME" )

echo "OK"
echo "DIR: $PKG_DIR"
echo "TAR: $OUT/${NAME}.tar.gz"