#!/usr/bin/env bash
set -euo pipefail
# Download core dirt-samples for offline rendering (idempotent)
# Usage: download-samples.sh [--force]
SAMPLES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/samples"
FORCE="${1:-}"
if [ "$FORCE" != "--force" ] && [ -d "$SAMPLES_DIR" ] && [ "$(find "$SAMPLES_DIR" -name '*.wav' 2>/dev/null | wc -l)" -gt 50 ]; then
  COUNT=$(find "$SAMPLES_DIR" -name '*.wav' | wc -l)
  echo "✅ Samples present ($COUNT files). Use --force to re-download."
  exit 0
fi
echo "Downloading dirt-samples..."
TMP=$(mktemp -d)
git clone --filter=blob:none --sparse https://github.com/tidalcycles/Dirt-Samples.git "$TMP" 2>&1
cd "$TMP"
git sparse-checkout set bd sd hh oh cp cr ride rim mt lt ht cb 808bd 808sd 808hc 808oh
mkdir -p "$SAMPLES_DIR"
for d in bd sd hh oh cp cr ride rim mt lt ht cb 808bd 808sd 808hc 808oh; do
  [ -d "$d" ] && cp -r "$d" "$SAMPLES_DIR/"
done
rm -rf "$TMP"
echo "✅ $(find "$SAMPLES_DIR" -name '*.wav' | wc -l) samples downloaded to $SAMPLES_DIR"
