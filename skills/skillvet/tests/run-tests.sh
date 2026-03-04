#!/usr/bin/env bash
# run-tests.sh — Test runner for skillvet
# Usage: bash tests/run-tests.sh
# Returns: 0 = all pass, 1 = failures
#
# Test fixtures are base64-encoded in fixtures.b64 to avoid
# antivirus false positives (the fixtures contain malware signatures
# that the scanner is designed to detect).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
AUDIT="$PROJECT_DIR/scripts/skill-audit.sh"
FIXTURES_B64="$SCRIPT_DIR/fixtures.b64"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

PASSED=0
FAILED=0
TOTAL=0

# --- Decode fixtures to temp directory ---
FIXTURES=$(mktemp -d)
trap 'rm -rf "$FIXTURES"' EXIT

decode_fixtures() {
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    [[ "$line" == \#* ]] && continue
    # Split on first = only (base64 content may contain = padding)
    local path="${line%%=*}"
    local encoded="${line#*=}"
    local dir="$FIXTURES/$(dirname "$path")"
    local file="$FIXTURES/$path"
    mkdir -p "$dir"
    echo "$encoded" | base64 -d > "$file"
  done < "$FIXTURES_B64"
}

echo "Decoding test fixtures..."
decode_fixtures
fixture_count=$(find "$FIXTURES" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
echo "Decoded $fixture_count fixtures to temp directory"
echo ""

# --- Test runner ---

run_test() {
  local name="$1"
  local fixture="$2"
  local expected_exit="$3"
  local expect_pattern="${4:-}"
  local reject_pattern="${5:-}"

  TOTAL=$((TOTAL + 1))

  output=$(bash "$AUDIT" --json "$fixture" 2>&1)
  actual_exit=$?

  local fail_reason=""

  if [ "$actual_exit" -ne "$expected_exit" ]; then
    fail_reason="exit code: expected $expected_exit, got $actual_exit"
  fi

  if [ -n "$expect_pattern" ] && ! echo "$output" | grep -qiE "$expect_pattern"; then
    fail_reason="${fail_reason:+$fail_reason; }expected pattern not found: $expect_pattern"
  fi

  if [ -n "$reject_pattern" ] && echo "$output" | grep -qiE "$reject_pattern"; then
    fail_reason="${fail_reason:+$fail_reason; }rejected pattern was found: $reject_pattern"
  fi

  if [ -z "$fail_reason" ]; then
    printf "${GREEN}PASS${NC} %s\n" "$name"
    PASSED=$((PASSED + 1))
  else
    printf "${RED}FAIL${NC} %s — %s\n" "$name" "$fail_reason"
    FAILED=$((FAILED + 1))
  fi
}

echo "Running skillvet tests..."
echo "---"

# Clean skill — should pass with no findings
run_test "clean-skill (exit 0)" \
  "$FIXTURES/clean-skill" 0 \
  '"critical":0' \
  ""

# --- Core Security Checks ---

# Check #1 — exfil endpoint
run_test "trigger-exfil-endpoint (exit 2, check #1)" \
  "$FIXTURES/trigger-exfil-endpoint" 2 \
  "exfiltration endpoint" \
  ""

# Check #2 — env theft
run_test "trigger-env-theft (exit 2, check #2)" \
  "$FIXTURES/trigger-env-theft" 2 \
  "env harvesting" \
  ""

# Check #3 — credential access
run_test "trigger-credential-access (exit 2, check #3)" \
  "$FIXTURES/trigger-credential-access" 2 \
  "foreign credentials" \
  ""

# Check #4 — obfuscation
run_test "trigger-obfuscation (exit 2, check #4)" \
  "$FIXTURES/trigger-obfuscation" 2 \
  "obfuscation" \
  ""

# Check #5 — path traversal
run_test "trigger-path-traversal (exit 2, check #5)" \
  "$FIXTURES/trigger-path-traversal" 2 \
  "path traversal" \
  ""

# Check #6 — exfil via curl/wget
run_test "trigger-exfil-curl (exit 2, check #6)" \
  "$FIXTURES/trigger-exfil-curl" 2 \
  "exfiltration pattern" \
  ""

# Check #7 — reverse shell
run_test "trigger-reverse-shell (exit 2, check #7)" \
  "$FIXTURES/trigger-reverse-shell" 2 \
  "reverse.*shell" \
  ""

# Check #8 — .env file theft
run_test "trigger-env-file-theft (exit 2, check #8)" \
  "$FIXTURES/trigger-env-file-theft" 2 \
  "env file access" \
  ""

# Check #9 — prompt injection
run_test "trigger-prompt-injection (exit 2, check #9)" \
  "$FIXTURES/trigger-prompt-injection" 2 \
  "prompt injection" \
  ""

# Check #10 — LLM tool exploitation
run_test "trigger-llm-exploitation (exit 2, check #10)" \
  "$FIXTURES/trigger-llm-exploitation" 2 \
  "LLM tool exploitation" \
  ""

# Check #11 — agent config tampering
run_test "trigger-config-tamper (exit 2, check #11)" \
  "$FIXTURES/trigger-config-tamper" 2 \
  "config tampering" \
  ""

# Check #12 — unicode obfuscation
run_test "trigger-unicode-obfuscation (exit 2, check #12)" \
  "$FIXTURES/trigger-unicode-obfuscation" 2 \
  "unicode obfuscation" \
  ""

# Check #13 — suspicious setup commands
run_test "trigger-setup-commands (exit 2, check #13)" \
  "$FIXTURES/trigger-setup-commands" 2 \
  "setup command" \
  ""

# Check #14 — social engineering
run_test "trigger-social-engineering (exit 2, check #14)" \
  "$FIXTURES/trigger-social-engineering" 2 \
  "social engineering" \
  ""

# Check #15 — shipped .env files
run_test "trigger-shipped-env (exit 2, check #15)" \
  "$FIXTURES/trigger-shipped-env" 2 \
  "env file shipped" \
  ""

# Check #16 — homograph characters
run_test "trigger-homograph (exit 2, check #16)" \
  "$FIXTURES/trigger-homograph" 2 \
  "homograph" \
  ""

# Check #17 — ANSI escape injection
run_test "trigger-ansi-escape (exit 2, check #17)" \
  "$FIXTURES/trigger-ansi-escape" 2 \
  "ansi escape" \
  ""

# Check #18 — punycode domains
run_test "trigger-punycode (exit 2, check #18)" \
  "$FIXTURES/trigger-punycode" 2 \
  "punycode" \
  ""

# Check #19 — double-encoded paths
run_test "trigger-double-encoded (exit 2, check #19)" \
  "$FIXTURES/trigger-double-encoded" 2 \
  "double.encoded" \
  ""

# Check #20 — shortened URLs
run_test "trigger-shortened-url (exit 2, check #20)" \
  "$FIXTURES/trigger-shortened-url" 2 \
  "shortened URL" \
  ""

# Check #21 — pipe-to-shell
run_test "trigger-pipe-to-shell (exit 2, check #21)" \
  "$FIXTURES/trigger-pipe-to-shell" 2 \
  "pipe.to.shell" \
  ""

# Check #22 — string construction evasion
run_test "trigger-string-evasion (exit 2, check #22)" \
  "$FIXTURES/trigger-string-evasion" 2 \
  "string construction evasion" \
  ""

# Check #23 — data flow chain analysis
run_test "trigger-chain-analysis (exit 2, check #23)" \
  "$FIXTURES/trigger-chain-analysis" 2 \
  "data flow chain" \
  ""

# Check #24 — time bomb detection
run_test "trigger-time-bomb (exit 2, check #24)" \
  "$FIXTURES/trigger-time-bomb" 2 \
  "time bomb" \
  ""

# --- Campaign-inspired checks ---

# Check #25 — IOC blocklist
run_test "trigger-ioc-blocklist (exit 2, check #25)" \
  "$FIXTURES/trigger-ioc-blocklist" 2 \
  "malicious C2 IP" \
  ""

# Check #26 — password-protected archive
run_test "trigger-password-archive (exit 2, check #26)" \
  "$FIXTURES/trigger-password-archive" 2 \
  "password.*archive" \
  ""

# Check #27 — paste service
run_test "trigger-paste-service (exit 2, check #27)" \
  "$FIXTURES/trigger-paste-service" 2 \
  "paste service" \
  ""

# Check #28 — GitHub releases binary
run_test "trigger-github-releases (exit 2, check #28)" \
  "$FIXTURES/trigger-github-releases" 2 \
  "GitHub releases binary" \
  ""

# Check #29 — base64 pipe-to-interpreter
run_test "trigger-base64-pipe (exit 2, check #29)" \
  "$FIXTURES/trigger-base64-pipe" 2 \
  "base64 pipe" \
  ""

# Check #30 — subprocess + network command
run_test "trigger-subprocess-network (exit 2, check #30)" \
  "$FIXTURES/trigger-subprocess-network" 2 \
  "subprocess.*network" \
  ""

# Check #31 — fake URL misdirection
run_test "trigger-fake-url-misdirect (exit 2, check #31)" \
  "$FIXTURES/trigger-fake-url-misdirect" 2 \
  "fake URL misdirection|decoy URL" \
  ""

# Check #32 — process persistence + network
run_test "trigger-persistence-network (exit 2, check #32)" \
  "$FIXTURES/trigger-persistence-network" 2 \
  "persistence.*network|backdoor" \
  ""

# Check #33 — fake prerequisite
run_test "trigger-fake-prerequisite (exit 2, check #33)" \
  "$FIXTURES/trigger-fake-prerequisite" 2 \
  "fake prerequisite|external download" \
  ""

# Check #34 — xattr/chmod dropper
run_test "trigger-xattr-dropper (exit 2, check #34)" \
  "$FIXTURES/trigger-xattr-dropper" 2 \
  "gatekeeper|xattr|chmod" \
  ""

# --- 1Password blog-inspired checks ---

# Check #35 — ClickFix download+execute chain
run_test "trigger-clickfix-chain (exit 2, check #35)" \
  "$FIXTURES/trigger-clickfix-chain" 2 \
  "clickfix|download.*execute" \
  ""

# Check #36 — suspicious package sources
run_test "trigger-suspicious-package (exit 2, check #36)" \
  "$FIXTURES/trigger-suspicious-package" 2 \
  "suspicious.*package|official registry" \
  ""

# Check #37 — staged installer pattern
run_test "trigger-staged-installer (exit 2, check #37)" \
  "$FIXTURES/trigger-staged-installer" 2 \
  "suspicious.*dependency|core.*base.*lib" \
  ""

# --- False positive tests ---

# False positive — educational prompt injection context
run_test "false-positive-prompt-injection (exit 0)" \
  "$FIXTURES/false-positive-prompt-injection" 0 \
  '"critical":0' \
  ""

# False positive — own declared keys
run_test "false-positive-own-keys (exit 0)" \
  "$FIXTURES/false-positive-own-keys" 0 \
  '"critical":0' \
  ""

echo "---"
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}, %d total\n" "$PASSED" "$FAILED" "$TOTAL"

if [ $FAILED -gt 0 ]; then
  exit 1
fi
exit 0
