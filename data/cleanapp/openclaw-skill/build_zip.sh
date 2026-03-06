#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$DIR/dist"
mkdir -p "$OUT_DIR"

name="cleanapp_ingest_skill"
ver="$(python3 -c 'import json; print(json.load(open("'"$DIR"'/manifest.json"))["version"])')"
zip_path="$OUT_DIR/${name}_${ver}.zip"

rm -f "$zip_path"

(
  cd "$DIR"
  zip -r "$zip_path" \
    manifest.json README.md SKILL.md run.sh ingest.py examples scripts references >/dev/null
)

echo "wrote $zip_path"
