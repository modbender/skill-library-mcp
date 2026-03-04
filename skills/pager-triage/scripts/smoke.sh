#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# smoke.sh — Quick smoke tests for pager-triage
#
# Verifies:
#   1. Script exists and is executable
#   2. Dependencies (curl, jq) are available
#   3. Help output works
#   4. Missing API key produces a clean error
#   5. Unknown subcommand produces a clean error
#   6. Invalid incident ID is rejected
#   7. No-args produces usage
#
# Usage: ./scripts/smoke.sh
# Exit: 0 if all pass, 1 on first failure
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL="${SCRIPT_DIR}/pager-triage.sh"

PASS=0
FAIL=0

pass() {
  PASS=$((PASS + 1))
  printf '  ✅ %s\n' "$1"
}

fail() {
  FAIL=$((FAIL + 1))
  printf '  ❌ %s\n' "$1"
}

section() {
  printf '\n🔍 %s\n' "$1"
}

# ---------------------------------------------------------------------------

section "Pre-flight checks"

if [[ -f "$TOOL" ]]; then
  pass "Script exists: $TOOL"
else
  fail "Script not found: $TOOL"
  echo "Cannot continue without the script."
  exit 1
fi

if [[ -x "$TOOL" ]]; then
  pass "Script is executable"
else
  fail "Script is not executable (run: chmod +x $TOOL)"
  exit 1
fi

if command -v curl &>/dev/null; then
  pass "curl is available"
else
  fail "curl is not installed"
fi

if command -v jq &>/dev/null; then
  pass "jq is available"
else
  fail "jq is not installed"
fi

# ---------------------------------------------------------------------------

section "Help output"

if output=$("$TOOL" help 2>&1); then
  if echo "$output" | grep -q "incidents"; then
    pass "Help mentions 'incidents' subcommand"
  else
    fail "Help output missing 'incidents'"
  fi
  if echo "$output" | grep -q "PAGERDUTY_API_KEY"; then
    pass "Help mentions PAGERDUTY_API_KEY"
  else
    fail "Help output missing PAGERDUTY_API_KEY"
  fi
else
  fail "Help command returned non-zero"
fi

# ---------------------------------------------------------------------------

section "No-arguments handling"

if "$TOOL" >/dev/null 2>&1; then
  fail "No-args should exit non-zero"
else
  pass "No-args exits non-zero"
fi

# ---------------------------------------------------------------------------

section "Unknown subcommand handling"

if output=$("$TOOL" this_does_not_exist 2>&1); then
  fail "Unknown subcommand should exit non-zero"
else
  if echo "$output" | grep -q "Unknown subcommand"; then
    pass "Unknown subcommand produces clean error"
  else
    fail "Unknown subcommand error message unclear: $output"
  fi
fi

# ---------------------------------------------------------------------------

section "Missing API key detection"

(
  unset PAGERDUTY_API_KEY 2>/dev/null || true
  if output=$("$TOOL" incidents 2>&1); then
    fail "Missing API key should exit non-zero"
  else
    if echo "$output" | grep -q "PAGERDUTY_API_KEY"; then
      pass "Missing API key error mentions PAGERDUTY_API_KEY"
    else
      fail "Missing API key error unclear: $output"
    fi
  fi
)

# ---------------------------------------------------------------------------

section "Input validation"

(
  export PAGERDUTY_API_KEY="smoke_test_key"
  if output=$("$TOOL" detail "../../etc/passwd" 2>&1); then
    fail "Path traversal ID should be rejected"
  else
    if echo "$output" | grep -q "Invalid incident ID"; then
      pass "Path traversal incident ID rejected"
    else
      fail "Unexpected error for path traversal ID: $output"
    fi
  fi
)

(
  export PAGERDUTY_API_KEY="smoke_test_key"
  if output=$("$TOOL" detail 'P123;rm -rf /' 2>&1); then
    fail "Command injection ID should be rejected"
  else
    if echo "$output" | grep -q "Invalid incident ID"; then
      pass "Command injection incident ID rejected"
    else
      fail "Unexpected error for injection ID: $output"
    fi
  fi
)

(
  export PAGERDUTY_API_KEY="smoke_test_key"
  if output=$("$TOOL" detail "" 2>&1); then
    fail "Empty incident ID should be rejected"
  else
    if echo "$output" | grep -q -i "usage\|incident_id"; then
      pass "Empty incident ID produces usage error"
    else
      fail "Unexpected error for empty ID: $output"
    fi
  fi
)

# ---------------------------------------------------------------------------

section "Missing email for write ops"

(
  export PAGERDUTY_API_KEY="smoke_test_key"
  unset PAGERDUTY_EMAIL 2>/dev/null || true
  if output=$("$TOOL" ack P123ABC --confirm 2>&1); then
    fail "Missing email should exit non-zero for write ops"
  else
    if echo "$output" | grep -q "PAGERDUTY_EMAIL"; then
      pass "Missing email error mentions PAGERDUTY_EMAIL"
    else
      fail "Missing email error unclear: $output"
    fi
  fi
)

# ---------------------------------------------------------------------------

section "Environment variable detection"

if [[ -n "${PAGERDUTY_API_KEY:-}" ]]; then
  pass "PAGERDUTY_API_KEY is set ($(echo "${PAGERDUTY_API_KEY}" | head -c 4)****)"
else
  echo "  ℹ️  PAGERDUTY_API_KEY not set — skipping live API tests (this is fine for smoke tests)"
fi

if [[ -n "${PAGERDUTY_EMAIL:-}" ]]; then
  pass "PAGERDUTY_EMAIL is set (${PAGERDUTY_EMAIL})"
else
  echo "  ℹ️  PAGERDUTY_EMAIL not set — write operations will require it"
fi

# ---------------------------------------------------------------------------

printf '\n─────────────────────────────\n'
printf '  Results: %d passed, %d failed\n' "$PASS" "$FAIL"
printf '─────────────────────────────\n'

if [[ "$FAIL" -gt 0 ]]; then
  exit 1
else
  printf '  🎉 All smoke tests passed!\n\n'
  exit 0
fi
