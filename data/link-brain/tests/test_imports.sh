#!/bin/bash
# Test all import formats for Link Brain v4.0.0
set -e

SCRIPT="$(dirname "$0")/../scripts/brain.py"
FIXTURES="$(dirname "$0")/fixtures"
export LINK_BRAIN_DIR=$(mktemp -d)
trap "rm -rf $LINK_BRAIN_DIR" EXIT

PASS=0
FAIL=0

check() {
    local desc="$1"
    local expected="$2"
    local output="$3"
    if echo "$output" | grep -q "$expected"; then
        echo "  PASS: $desc"
        PASS=$((PASS+1))
    else
        echo "  FAIL: $desc (expected '$expected')"
        echo "  Output: $output"
        FAIL=$((FAIL+1))
    fi
}

echo "=== Link Brain v4.0.0 Import Tests ==="
echo "Data dir: $LINK_BRAIN_DIR"
echo

# Setup
echo "--- setup ---"
OUT=$(python3 "$SCRIPT" setup 2>&1)
check "setup creates dir" "Created" "$OUT"
OUT=$(python3 "$SCRIPT" setup 2>&1)
check "setup idempotent" "Already set up" "$OUT"

# Help
echo "--- help ---"
OUT=$(python3 "$SCRIPT" help 2>&1)
check "help shows version" "v4.0.0" "$OUT"
check "help shows import sources" "YouTube" "$OUT"

# YouTube import
echo "--- youtube ---"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/youtube-history.json" --source youtube 2>&1)
check "youtube imports" '"imported": 2' "$OUT"
# Duplicate detection
OUT=$(python3 "$SCRIPT" import "$FIXTURES/youtube-history.json" --source youtube 2>&1)
check "youtube skips dupes" '"imported": 0' "$OUT"

# Reddit import
echo "--- reddit ---"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/reddit-saved.csv" --source reddit 2>&1)
check "reddit imports" '"imported": 2' "$OUT"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/reddit-saved.csv" --source reddit 2>&1)
check "reddit skips dupes" '"imported": 0' "$OUT"

# Pocket import
echo "--- pocket ---"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/pocket-export.html" --source pocket 2>&1)
check "pocket imports" '"imported": 3' "$OUT"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/pocket-export.html" --source pocket 2>&1)
check "pocket skips dupes" '"imported": 0' "$OUT"

# Instapaper import
echo "--- instapaper ---"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/instapaper-export.csv" --source instapaper 2>&1)
check "instapaper imports" '"imported": 3' "$OUT"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/instapaper-export.csv" --source instapaper 2>&1)
check "instapaper skips dupes" '"imported": 0' "$OUT"

# Raindrop CSV import
echo "--- raindrop csv ---"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/raindrop-export.csv" --source raindrop 2>&1)
check "raindrop csv imports" '"imported": 2' "$OUT"

# Raindrop HTML import
echo "--- raindrop html ---"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/raindrop-export.html" --source raindrop 2>&1)
check "raindrop html imports" '"imported": 2' "$OUT"

# Hacker News import
echo "--- hackernews ---"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/hackernews-favorites.json" --source hackernews 2>&1)
check "hackernews imports" '"imported":' "$OUT"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/hackernews-favorites.json" --source hackernews 2>&1)
check "hackernews skips dupes" '"imported": 0' "$OUT"

# Auto-detect
echo "--- auto-detect ---"
export LINK_BRAIN_DIR=$(mktemp -d)
OUT=$(python3 "$SCRIPT" import "$FIXTURES/youtube-history.json" 2>&1)
check "auto-detect youtube" '"source": "youtube"' "$OUT"
OUT=$(python3 "$SCRIPT" import "$FIXTURES/pocket-export.html" 2>&1)
check "auto-detect pocket" '"source": "pocket"' "$OUT"

# Stats
echo "--- stats ---"
OUT=$(python3 "$SCRIPT" stats 2>&1)
check "stats works" '"total_links"' "$OUT"

# Search
echo "--- search ---"
OUT=$(python3 "$SCRIPT" search "batteries" 2>&1)
check "search works" "youtube.com" "$OUT"

echo
echo "=== Results: $PASS passed, $FAIL failed ==="
[ $FAIL -eq 0 ] && echo "All tests passed!" || exit 1
