#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VERSION="$(sed -nE 's/^[[:space:]]*"version":[[:space:]]*"([^"]+)".*/\1/p' package.json | head -n1)"
if [[ -z "${VERSION}" ]]; then
  echo "Failed to read version from package.json" >&2
  exit 1
fi

OUT_PATH="${1:-/tmp/agent-registry-v${VERSION}.zip}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

MANIFEST="$TMP_DIR/files.txt"
git -c core.fsmonitor=false ls-files | LC_ALL=C sort > "$MANIFEST"

zip -X -q "$OUT_PATH" -@ < "$MANIFEST"

SHA256="$(shasum -a 256 "$OUT_PATH" | awk '{print $1}')"
BYTES="$(wc -c < "$OUT_PATH" | tr -d '[:space:]')"

echo "Artifact: $OUT_PATH"
echo "Version:  $VERSION"
echo "SHA256:   $SHA256"
echo "Size:     $BYTES bytes"
