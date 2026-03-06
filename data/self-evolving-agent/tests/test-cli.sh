#!/usr/bin/env bash
# ============================================================
# tests/test-cli.sh — Self-Evolving Agent CLI Tests
#
# Tests `sea` CLI commands against the actual bin/sea interface.
# Exit 0 = all pass, Exit 1 = failures
# ============================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SEA_BIN="$SKILL_DIR/bin/sea"

# Temp dir for this test run
TEST_TMP=$(mktemp -d)
trap 'rm -rf "$TEST_TMP"' EXIT

# ── Test counters ─────────────────────────────────────────────
PASS=0
FAIL=0
FAIL_MSGS=""

# ── Helpers ──────────────────────────────────────────────────
pass() { echo "  ✓ $1"; PASS=$((PASS + 1)); }
fail() {
  echo "  ✗ $1"
  FAIL=$((FAIL + 1))
  FAIL_MSGS="${FAIL_MSGS}\n  - $1"
}

assert() {
  local desc="$1"
  local condition="$2"
  if eval "$condition" 2>/dev/null; then
    pass "$desc"
  else
    fail "$desc"
  fi
}

assert_output_contains() {
  local desc="$1"
  local output="$2"
  local pattern="$3"
  if echo "$output" | grep -qi "$pattern" 2>/dev/null; then
    pass "$desc"
  else
    fail "$desc (output did not contain: '$pattern')"
  fi
}

assert_exit_zero() {
  local desc="$1"
  local cmd="$2"
  if eval "$cmd" > /dev/null 2>&1; then
    pass "$desc"
  else
    fail "$desc (non-zero exit)"
  fi
}

assert_exit_nonzero() {
  local desc="$1"
  local cmd="$2"
  if eval "$cmd" > /dev/null 2>&1; then
    fail "$desc (expected non-zero exit but got zero)"
  else
    pass "$desc"
  fi
}

section() { echo ""; echo "=== $1 ==="; }

# ============================================================
# Pre-check: sea binary
# ============================================================
section "Pre-check"

assert "bin/sea exists"        "[ -f '$SEA_BIN' ]"
assert "bin/sea is executable" "[ -x '$SEA_BIN' ]"
assert "bin/sea is a bash script" "head -1 '$SEA_BIN' | grep -q 'bash'"

if [ ! -x "$SEA_BIN" ]; then
  echo ""
  echo "FATAL: $SEA_BIN is not executable. Cannot run CLI tests."
  echo "Run: chmod +x $SEA_BIN"
  echo ""
  echo "Results: ${PASS} passed, ${FAIL} failed"
  exit 1
fi

# ============================================================
# TEST 1: sea version
# ============================================================
section "Test 1: sea version"

VERSION_OUT=$("$SEA_BIN" version 2>/dev/null) || true
assert_exit_zero         "sea version exits 0"                    "'$SEA_BIN' version"
assert_output_contains   "sea version contains 'sea'"             "$VERSION_OUT" "sea"
assert_output_contains   "sea version contains version number"    "$VERSION_OUT" "[0-9]\+\.[0-9]\+"

# Also test --version and -v aliases
VERSION_ALIAS=$("$SEA_BIN" --version 2>/dev/null) || true
assert_output_contains   "sea --version works"                    "$VERSION_ALIAS" "sea\|version\|[0-9]\."

VERSION_V=$("$SEA_BIN" -v 2>/dev/null) || true
assert_output_contains   "sea -v works"                           "$VERSION_V" "sea\|version\|[0-9]\."

# ============================================================
# TEST 2: sea help
# ============================================================
section "Test 2: sea help"

HELP_OUT=$("$SEA_BIN" help 2>/dev/null) || true
assert_exit_zero       "sea help exits 0"                         "'$SEA_BIN' help"
assert_output_contains "sea help shows Usage line"                "$HELP_OUT" "Usage\|usage\|USAGE"
assert_output_contains "sea help lists 'version' command"         "$HELP_OUT" "version"
assert_output_contains "sea help lists 'health' command"          "$HELP_OUT" "health"
assert_output_contains "sea help lists 'status' command"          "$HELP_OUT" "status"
assert_output_contains "sea help lists 'config' command"          "$HELP_OUT" "config"
assert_output_contains "sea help lists 'run' command"             "$HELP_OUT" "run"

# --help and -h aliases
HELP_ALIAS=$("$SEA_BIN" --help 2>/dev/null) || true
assert_output_contains "sea --help works"                         "$HELP_ALIAS" "Usage\|usage\|USAGE"

HELP_H=$("$SEA_BIN" -h 2>/dev/null) || true
assert_output_contains "sea -h works"                             "$HELP_H" "Usage\|usage\|USAGE"

# ============================================================
# TEST 3: sea status
# ============================================================
section "Test 3: sea status"

STATUS_OUT=$("$SEA_BIN" status 2>/dev/null) || true
assert_exit_zero       "sea status exits 0"                       "'$SEA_BIN' status"
assert_output_contains "sea status shows proposals info"          "$STATUS_OUT" "Proposals\|proposals\|Last run\|Sessions"

# sea status --json should produce valid JSON
STATUS_JSON=$("$SEA_BIN" status --json 2>/dev/null) || true
assert_output_contains "sea status --json produces JSON"          "$STATUS_JSON" "{"
assert "sea status --json is valid JSON" \
  "python3 -c 'import json; json.loads(\"\"\"$STATUS_JSON\"\"\")' 2>/dev/null || python3 -c 'import json; json.loads(open(\"/dev/stdin\").read())' <<< '$STATUS_JSON' 2>/dev/null || echo '$STATUS_JSON' | python3 -c 'import json,sys; json.load(sys.stdin)'"

# Test with no existing run data (clean TMP_DIR)
STATUS_NORUN=$("$SEA_BIN" status 2>/dev/null) || true
# Should still produce output even with no run history
assert_output_contains "sea status works with no run history"     "$STATUS_NORUN" "Last run\|Proposals\|Sessions"

# ============================================================
# TEST 4: sea health
# ============================================================
section "Test 4: sea health"

# health exits 0 (it's informational, not a pass/fail check)
HEALTH_OUT=$("$SEA_BIN" health 2>/dev/null) || true
assert_exit_zero       "sea health exits 0"                       "'$SEA_BIN' health"
assert_output_contains "sea health shows AGENTS.md info"          "$HEALTH_OUT" "AGENTS.md\|health\|Health"
assert_output_contains "sea health shows score"                   "$HEALTH_OUT" "/10\|score\|Score"

# health --json should produce valid JSON
HEALTH_JSON=$("$SEA_BIN" health --json 2>/dev/null) || true
assert_output_contains "sea health --json produces JSON"          "$HEALTH_JSON" "{"
_HJ_VALID=$(echo "$HEALTH_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print('ok')" 2>/dev/null || echo "fail")
assert "sea health --json is valid JSON"                          "[ '$_HJ_VALID' = 'ok' ]"

# ============================================================
# TEST 5: sea config
# ============================================================
section "Test 5: sea config"

# sea config (no args) → shows config.yaml contents
CONFIG_OUT=$("$SEA_BIN" config 2>/dev/null) || true
assert_exit_zero       "sea config exits 0"                       "'$SEA_BIN' config"
assert_output_contains "sea config shows analysis section"        "$CONFIG_OUT" "analysis\|analysis:"
assert_output_contains "sea config shows proposals section"       "$CONFIG_OUT" "proposals\|proposals:"

# sea config --json → valid JSON
CONFIG_JSON=$("$SEA_BIN" config --json 2>/dev/null) || true
assert_output_contains "sea config --json produces JSON"          "$CONFIG_JSON" "{"
_CJ_VALID=$(echo "$CONFIG_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print('ok')" 2>/dev/null || echo "fail")
assert "sea config --json is valid JSON"                          "[ '$_CJ_VALID' = 'ok' ]"

# sea config set key val → updates value, shows confirmation
# Use a non-critical value (verbose) to avoid breaking the config
CONFIG_SET_OUT=$("$SEA_BIN" config set output.verbose true 2>/dev/null) || true
assert_output_contains "sea config set shows confirmation"        "$CONFIG_SET_OUT" "Updated\|✅\|updated\|set"

# sea config set (no args) → error exit
assert_exit_nonzero    "sea config set (no args) exits non-zero"  "'$SEA_BIN' config set"

# sea config set (missing value) → error exit
assert_exit_nonzero    "sea config set (missing val) exits non-zero" "'$SEA_BIN' config set analysis.days"

# ============================================================
# TEST 6: sea proposals (with fixture data)
# ============================================================
section "Test 6: sea proposals"

# Set up a temp skill with fixture proposals
PROP_SKILL="$TEST_TMP/prop-skill"
mkdir -p "$PROP_SKILL/bin" "$PROP_SKILL/data/proposals"
cp "$SEA_BIN" "$PROP_SKILL/bin/sea"
cp "$SKILL_DIR/config.yaml" "$PROP_SKILL/config.yaml"  2>/dev/null || true
cp "$SKILL_DIR/_meta.json"  "$PROP_SKILL/_meta.json"   2>/dev/null || true

# Copy fixture proposals (3 proposals: applied, rejected, pending)
python3 - "$SCRIPT_DIR/fixtures/mock-proposals.json" "$PROP_SKILL/data/proposals" << 'PYEOF' 2>/dev/null || true
import json, os
proposals = json.load(open(__import__('sys').argv[1]))
for p in proposals:
    pid = p.get('id', 'unknown')
    fname = f"{pid}.json"
    with open(os.path.join(__import__('sys').argv[2], fname), 'w') as f:
        json.dump(p, f, indent=2)
PYEOF

# sea proposals → list pending only
PROP_OUT=$("$PROP_SKILL/bin/sea" proposals 2>/dev/null) || true
assert_output_contains "sea proposals lists pending items" "$PROP_OUT" "pending\|Pending\|proposal\|Proposal\|WAL\|enforce"

# sea proposals --all → all proposals
PROP_ALL=$("$PROP_SKILL/bin/sea" proposals --all 2>/dev/null) || true
assert_output_contains "sea proposals --all shows multiple entries" "$PROP_ALL" "applied\|rejected\|pending\|WAL\|heartbeat\|git"

# sea history → all proposals in history format
HIST_OUT=$("$PROP_SKILL/bin/sea" history 2>/dev/null) || true
assert_output_contains "sea history shows proposals" "$HIST_OUT" "WAL\|git\|heartbeat\|proposal\|[0-9]\{4\}"

# sea proposals --json → valid JSON array
PROP_JSON=$("$PROP_SKILL/bin/sea" proposals --json 2>/dev/null) || true
_PJ_VALID=$(echo "$PROP_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print('ok')" 2>/dev/null || echo "fail")
assert "sea proposals --json is valid JSON" "[ '$_PJ_VALID' = 'ok' ]"

# ============================================================
# TEST 7: Unknown command
# ============================================================
section "Test 7: Unknown command handling"

UNKNOWN_OUT=$("$SEA_BIN" unknowncommand 2>&1) || true
assert_output_contains "unknown command shows error or help" \
  "$UNKNOWN_OUT" "Unknown\|unknown\|command\|help\|Usage"

assert_exit_nonzero "unknown command exits non-zero" \
  "'$SEA_BIN' unknowncommand"

# ============================================================
# TEST 8: sea with empty data directory
# ============================================================
section "Test 8: Empty data directory"

EMPTY_DATA="$TEST_TMP/empty-data-skill"
mkdir -p "$EMPTY_DATA/bin" "$EMPTY_DATA/data/proposals"
cp "$SEA_BIN" "$EMPTY_DATA/bin/sea"
cp "$SKILL_DIR/config.yaml" "$EMPTY_DATA/config.yaml" 2>/dev/null || true
cp "$SKILL_DIR/_meta.json"  "$EMPTY_DATA/_meta.json"  2>/dev/null || echo '{"version":"1.0.0"}' > "$EMPTY_DATA/_meta.json"

# version should always work
EMPTY_VERSION=$("$EMPTY_DATA/bin/sea" version 2>/dev/null) || true
assert_output_contains "sea version works without data" "$EMPTY_VERSION" "sea\|v[0-9]\|CLI"

# help should always work
EMPTY_HELP=$("$EMPTY_DATA/bin/sea" help 2>/dev/null) || true
assert_output_contains "sea help works without data" "$EMPTY_HELP" "Usage\|usage\|USAGE"

# status with no proposals (empty dir)
EMPTY_STATUS=$("$EMPTY_DATA/bin/sea" status 2>/dev/null) || true
assert_output_contains "sea status works with empty proposals dir" \
  "$EMPTY_STATUS" "Proposals\|proposals\|0\|Last run"

# proposals with empty dir → no proposals message
EMPTY_PROPS=$("$EMPTY_DATA/bin/sea" proposals 2>/dev/null) || true
assert_output_contains "sea proposals shows no-proposals message for empty dir" \
  "$EMPTY_PROPS" "No\|no\|none\|0\|empty\|found"

# ============================================================
# RESULTS
# ============================================================
echo ""
echo "=============================="
echo "Results: ${PASS} passed, ${FAIL} failed"
if [ -n "$FAIL_MSGS" ]; then
  echo -e "Failures:${FAIL_MSGS}"
fi
echo "=============================="

[ "$FAIL" -eq 0 ]
