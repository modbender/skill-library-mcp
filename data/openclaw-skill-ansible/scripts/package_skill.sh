#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR=$1
VERSION=${2:-0.0.0}
OUT=${3:-/tmp}
NAME=$(basename "$SKILL_DIR")
TAR="$OUT/${NAME}-${VERSION}.tar.gz"
sha256sum() { sha256 -a 256 "$1" 2>/dev/null || shasum -a 256 "$1"; }

echo "Packaging $SKILL_DIR -> $TAR"
cd $(dirname "$SKILL_DIR")
tar -czf "$TAR" "$(basename "$SKILL_DIR")"
SHA=$(sha256sum "$TAR" | awk '{print $1}')
echo "$SHA  $TAR" > "$TAR.sha256"
ls -lh "$TAR"
echo "Wrote $TAR and $TAR.sha256"
