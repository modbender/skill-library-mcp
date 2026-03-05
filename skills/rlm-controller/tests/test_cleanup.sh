#!/usr/bin/env bash
# Tests for cleanup.sh — retention, ignore rules, scratch-path confinement.
# Uses non-sensitive sample data only.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLEANUP="$REPO_DIR/scripts/cleanup.sh"

PASS=0
FAIL=0

assert_file_exists() {
  if [[ -f "$1" ]]; then
    PASS=$((PASS+1))
  else
    FAIL=$((FAIL+1))
    echo "FAIL: expected file to exist: $1"
  fi
}

assert_file_missing() {
  if [[ ! -f "$1" ]]; then
    PASS=$((PASS+1))
  else
    FAIL=$((FAIL+1))
    echo "FAIL: expected file to be deleted: $1"
  fi
}

# ---------------------------------------------------------------
# Setup: create a temporary workspace with scratch structure
# ---------------------------------------------------------------
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

SCRATCH="$WORK_DIR/scratch/rlm_prototype"
CTX_DIR="$SCRATCH/ctx"
LOG_DIR="$SCRATCH/logs"
mkdir -p "$CTX_DIR" "$LOG_DIR"

# Populate with non-sensitive sample files
echo "sample context alpha" > "$CTX_DIR/alpha.txt"
echo "sample context beta"  > "$CTX_DIR/beta.txt"
echo '{"action":"peek"}'    > "$LOG_DIR/run_001.jsonl"
echo '{"action":"search"}'  > "$LOG_DIR/run_002.jsonl"
echo '{"action":"chunk"}'   > "$LOG_DIR/run_003.jsonl"

# ---------------------------------------------------------------
# Test 1: RETENTION=0 deletes all files (no ignore rules)
# ---------------------------------------------------------------
echo "--- Test 1: RETENTION=0, no ignore rules ---"
CLEAN_ROOT="$WORK_DIR" CLEAN_RETENTION=0 CLEAN_IGNORE_FILE=/dev/null \
  bash "$CLEANUP" > /dev/null

assert_file_missing "$CTX_DIR/alpha.txt"
assert_file_missing "$CTX_DIR/beta.txt"
assert_file_missing "$LOG_DIR/run_001.jsonl"
assert_file_missing "$LOG_DIR/run_002.jsonl"
assert_file_missing "$LOG_DIR/run_003.jsonl"

# ---------------------------------------------------------------
# Test 2: RETENTION=0 with ignore rules preserves matching files
# ---------------------------------------------------------------
echo "--- Test 2: RETENTION=0, ignore rule matches 'alpha' ---"
# Re-create files
echo "sample context alpha" > "$CTX_DIR/alpha.txt"
echo "sample context beta"  > "$CTX_DIR/beta.txt"
echo '{"action":"peek"}'    > "$LOG_DIR/run_001.jsonl"

IGNORE_TMP="$WORK_DIR/ignore.txt"
echo "alpha" > "$IGNORE_TMP"

CLEAN_ROOT="$WORK_DIR" CLEAN_RETENTION=0 CLEAN_IGNORE_FILE="$IGNORE_TMP" \
  bash "$CLEANUP" > /dev/null

assert_file_exists  "$CTX_DIR/alpha.txt"    # matches ignore rule
assert_file_missing "$CTX_DIR/beta.txt"     # does not match
assert_file_missing "$LOG_DIR/run_001.jsonl"

# ---------------------------------------------------------------
# Test 3: RETENTION=2 keeps last 2 files by mtime
# ---------------------------------------------------------------
echo "--- Test 3: RETENTION=2, keeps newest 2 files ---"
# Re-create with different mtimes using explicit timestamps
echo "old"    > "$LOG_DIR/run_A.jsonl"; touch -t 202501010000 "$LOG_DIR/run_A.jsonl"
echo "mid"    > "$LOG_DIR/run_B.jsonl"; touch -t 202501020000 "$LOG_DIR/run_B.jsonl"
echo "newest" > "$LOG_DIR/run_C.jsonl"; touch -t 202501030000 "$LOG_DIR/run_C.jsonl"

CLEAN_ROOT="$WORK_DIR" CLEAN_RETENTION=2 CLEAN_IGNORE_FILE=/dev/null \
  bash "$CLEANUP" > /dev/null

# newest 2 should survive; oldest deleted
assert_file_exists  "$LOG_DIR/run_C.jsonl"
assert_file_exists  "$LOG_DIR/run_B.jsonl"
assert_file_missing "$LOG_DIR/run_A.jsonl"

# ---------------------------------------------------------------
# Test 4: Scratch path confinement — files outside scratch are untouched
# ---------------------------------------------------------------
echo "--- Test 4: Files outside scratch/ are not affected ---"
echo "outside" > "$WORK_DIR/outside.txt"

CLEAN_ROOT="$WORK_DIR" CLEAN_RETENTION=0 CLEAN_IGNORE_FILE=/dev/null \
  bash "$CLEANUP" > /dev/null

assert_file_exists "$WORK_DIR/outside.txt"

# ---------------------------------------------------------------
# Test 5: Missing directories do not cause errors
# ---------------------------------------------------------------
echo "--- Test 5: Missing target directories handled gracefully ---"
EMPTY_DIR="$(mktemp -d)"
CLEAN_ROOT="$EMPTY_DIR" CLEAN_RETENTION=0 CLEAN_IGNORE_FILE=/dev/null \
  bash "$CLEANUP" > /dev/null
# If we get here without error, the test passes
PASS=$((PASS+1))
rm -rf "$EMPTY_DIR"

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
echo ""
echo "=== cleanup.sh test results ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
echo "All tests passed."
