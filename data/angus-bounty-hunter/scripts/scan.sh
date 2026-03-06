#!/bin/bash
# Bounty Hunter — Automated Slither scan
# Usage: bash scripts/scan.sh <repo-url> [src-dir]
set -e

REPO_URL="$1"
SRC_DIR="${2:-src}"

if [ -z "$REPO_URL" ]; then
  echo "Usage: bash scripts/scan.sh <repo-url> [src-dir]"
  exit 1
fi

REPO_NAME=$(basename "$REPO_URL" .git)
WORK_DIR="${BOUNTY_WORKDIR:-/tmp/bounty-scans}"
OUTPUT_DIR="${BOUNTY_OUTPUT:-./bounty-results}"

mkdir -p "$WORK_DIR" "$OUTPUT_DIR"

# Clone
cd "$WORK_DIR"
if [ -d "$REPO_NAME" ]; then
  echo "[*] Repo exists, pulling..."
  cd "$REPO_NAME" && git pull --depth 1 2>/dev/null || true
else
  echo "[*] Cloning $REPO_URL..."
  git clone --depth 1 "$REPO_URL" 2>&1
  cd "$REPO_NAME"
fi

# Detect and install solc version
SOLC_VER=$(grep -rh "pragma solidity" "$SRC_DIR" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -1)
if [ -n "$SOLC_VER" ]; then
  echo "[*] Installing solc $SOLC_VER..."
  solc-select install "$SOLC_VER" 2>/dev/null || true
  solc-select use "$SOLC_VER" 2>/dev/null || true
fi

# Install deps
[ -f "package.json" ] && npm install --silent 2>/dev/null || true
[ -f "requirements.txt" ] && pip3 install -r requirements.txt --quiet 2>/dev/null || true

# Run Slither — full JSON output
echo "[*] Running Slither on $SRC_DIR..."
slither . \
  --filter-paths "test|mock|lib|node_modules" \
  --json "$OUTPUT_DIR/${REPO_NAME}-slither.json" \
  2>&1 | tee "$OUTPUT_DIR/${REPO_NAME}-slither.txt" || true

# Summary
echo ""
echo "=== RESULTS ==="
HIGHS=$(python3 -c "import json; d=json.load(open('$OUTPUT_DIR/${REPO_NAME}-slither.json')); print(len([x for x in d.get('results',{}).get('detectors',[]) if x.get('impact') in ['High','Medium']]))" 2>/dev/null || echo "?")
echo "HIGH/MEDIUM findings: $HIGHS"
echo "Full results: $OUTPUT_DIR/${REPO_NAME}-slither.json"
echo "Text output: $OUTPUT_DIR/${REPO_NAME}-slither.txt"
