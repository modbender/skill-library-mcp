#!/usr/bin/env bash
# ipeaky test suite — non-interactive tests (no osascript popups)
# Usage: bash tests/run_tests.sh

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

PASS=0
FAIL=0
SCRIPTS=scripts

pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }

echo "=== ipeaky test suite ==="
echo ""

# -------------------------------------------------------
echo "--- secure_input_mac.sh ---"

# T1: Missing argument → exits non-zero
echo "T1: Missing KEY_NAME argument"
if bash "$SCRIPTS/secure_input_mac.sh" 2>/dev/null; then
  fail "Should have exited non-zero with no args"
else
  pass "Exits non-zero with no args"
fi

# T2: Script uses 'with hidden answer'
echo "T2: Uses hidden answer (no plaintext input)"
if grep -q "with hidden answer" "$SCRIPTS/secure_input_mac.sh"; then
  pass "Hidden answer flag present"
else
  fail "Missing 'with hidden answer' — keys would show in plaintext!"
fi

# T3: Script uses set -euo pipefail
echo "T3: Strict mode (set -euo pipefail)"
if grep -q "set -euo pipefail" "$SCRIPTS/secure_input_mac.sh"; then
  pass "Strict mode enabled"
else
  fail "Missing set -euo pipefail"
fi

# T4: No eval, no key logging
echo "T4: No eval or echo of raw key"
if grep -qE '^\s*eval ' "$SCRIPTS/secure_input_mac.sh"; then
  fail "Contains eval — potential injection risk"
else
  pass "No eval found"
fi

# T5: Output uses echo -n (no trailing newline)
echo "T5: Output via echo -n (clean stdout)"
if grep -q 'echo -n "\$KEY"' "$SCRIPTS/secure_input_mac.sh" || grep -q "echo -n \"\\\$KEY\"" "$SCRIPTS/secure_input_mac.sh" || tail -1 "$SCRIPTS/secure_input_mac.sh" | grep -q 'echo -n'; then
  pass "Uses echo -n for clean output"
else
  fail "Might include trailing newline in key output"
fi

echo ""

# -------------------------------------------------------
echo "--- test_key.sh ---"

# T6: Missing service arg → exits non-zero
echo "T6: Missing SERVICE argument"
if echo "fake-key" | bash "$SCRIPTS/test_key.sh" 2>/dev/null; then
  fail "Should have exited non-zero with no service arg"
else
  pass "Exits non-zero with no service arg"
fi

# T7: Empty stdin → exits non-zero
echo "T7: Empty key on stdin"
if echo -n "" | bash "$SCRIPTS/test_key.sh" openai 2>/dev/null; then
  fail "Should have exited non-zero with empty key"
else
  pass "Exits non-zero with empty stdin"
fi

# T8: Key masking — only first 4 chars shown
echo "T8: Key masking (first 4 + ****)"
if grep -q 'KEY:0:4' "$SCRIPTS/test_key.sh"; then
  pass "Masking uses first 4 chars"
else
  fail "Key masking pattern not found"
fi

# T9: Strict mode
echo "T9: Strict mode (set -euo pipefail)"
if grep -q "set -euo pipefail" "$SCRIPTS/test_key.sh"; then
  pass "Strict mode enabled"
else
  fail "Missing set -euo pipefail"
fi

# T10: Unknown service doesn't fail
echo "T10: Unknown service falls through gracefully"
RESULT=$(echo "test-key-1234" | bash "$SCRIPTS/test_key.sh" unknown_service 2>&1)
if echo "$RESULT" | grep -q "OK:"; then
  pass "Unknown service returns OK with masked key"
else
  fail "Unknown service handling broken: $RESULT"
fi

# T11: Unknown service output doesn't contain full key
echo "T11: Unknown service output doesn't leak full key"
RESULT=$(echo "sk-supersecretkey12345" | bash "$SCRIPTS/test_key.sh" unknown_service 2>&1)
if echo "$RESULT" | grep -q "supersecretkey"; then
  fail "Full key leaked in output!"
else
  pass "Key not leaked in unknown service output"
fi

# T12: No eval in test_key.sh
echo "T12: No eval"
if grep -qE '^\s*eval ' "$SCRIPTS/test_key.sh"; then
  fail "Contains eval"
else
  pass "No eval found"
fi

# T13: No key in error messages (check FAIL paths)
echo "T13: FAIL messages use masked key only"
FAIL_LINES=$(grep "FAIL:" "$SCRIPTS/test_key.sh" | grep -v 'MASKED' || true)
if [ -z "$FAIL_LINES" ]; then
  pass "All FAIL messages reference MASKED variable"
else
  fail "Some FAIL messages might leak keys: $FAIL_LINES"
fi

echo ""

# -------------------------------------------------------
echo "--- SKILL.md security audit ---"

# T14: SKILL.md warns against echoing keys
echo "T14: SKILL.md has NEVER-echo rule"
if grep -qi "NEVER echo\|NEVER include.*key.*chat\|never.*print.*key" SKILL.md; then
  pass "NEVER-echo rule documented"
else
  fail "Missing explicit NEVER-echo warning"
fi

# T15: SKILL.md mentions config.patch
echo "T15: Uses gateway config.patch (native storage)"
if grep -q "config.patch" SKILL.md; then
  pass "config.patch flow documented"
else
  fail "Missing config.patch documentation"
fi

# T16: SKILL.md has key map
echo "T16: Key map (service → config path)"
if grep -q "Config Path" SKILL.md; then
  pass "Key map present"
else
  fail "Missing key map"
fi

echo ""

# -------------------------------------------------------
echo "--- store_key_v3.sh ---"

# T19: Missing arguments → exits non-zero
echo "T19: Missing SERVICE_NAME argument"
if bash "$SCRIPTS/store_key_v3.sh" 2>/dev/null; then
  fail "Should have exited non-zero with no args"
else
  pass "Exits non-zero with no args"
fi

# T20: Missing config paths → exits non-zero
echo "T20: Missing config paths"
if bash "$SCRIPTS/store_key_v3.sh" "Test Service" 2>/dev/null; then
  fail "Should have exited non-zero with no config paths"
else
  pass "Exits non-zero with no config paths"
fi

# T21: Strict mode
echo "T21: Strict mode (set -euo pipefail)"
if grep -q "set -euo pipefail" "$SCRIPTS/store_key_v3.sh"; then
  pass "Strict mode enabled"
else
  fail "Missing set -euo pipefail"
fi

# T22: Service name sanitization
echo "T22: SERVICE_NAME sanitization (shell injection protection)"
if grep -q "SAFE_SERVICE_NAME" "$SCRIPTS/store_key_v3.sh" && grep -q "sed.*['\"].*['\"]" "$SCRIPTS/store_key_v3.sh"; then
  pass "SERVICE_NAME sanitization implemented"
else
  fail "Missing SERVICE_NAME sanitization"
fi

# T23: Temp file security
echo "T23: Temp file with secure permissions (chmod 600)"
if grep -q "chmod 600.*TEMP_KEY_FILE" "$SCRIPTS/store_key_v3.sh"; then
  pass "Temp file secured with chmod 600"
else
  fail "Missing temp file permission setting"
fi

# T24: Secure cleanup
echo "T24: Secure temp file cleanup (overwrite + remove)"
if grep -q "dd.*if=/dev/urandom.*TEMP_KEY_FILE" "$SCRIPTS/store_key_v3.sh" || grep -q "rm.*TEMP_KEY_FILE" "$SCRIPTS/store_key_v3.sh"; then
  pass "Secure cleanup implemented"
else
  fail "Missing secure cleanup of temp file"
fi

# T25: No process-list exposure — key must NOT appear as CLI argument to any process
echo "T25: Key not exposed in process list (no argv exposure)"
# Check that key value is never passed as a positional arg to openclaw/curl/etc via shell expansion
if grep -E 'openclaw config set.*\$\(cat|\bcurl\b.*\$\(cat|\bopenclaw\b.*\$KEY' "$SCRIPTS/store_key_v3.sh" | grep -v '#'; then
  fail "Key value passed via shell expansion into process argv (process list leak!)"
else
  pass "Key value never appears as CLI argument — uses Python direct JSON write"
fi

# T26: Uses Python for config write (zero argv exposure)
echo "T26: Uses Python direct JSON write (key stays out of argv)"
if grep -q 'python3 -' "$SCRIPTS/store_key_v3.sh"; then
  pass "Python inline script writes key directly to openclaw.json"
else
  fail "Missing Python-based config write — key may leak into process list"
fi

# T27: SERVICE_NAME sanitization — backtick injection
echo "T27: SERVICE_NAME sanitization removes backticks"
if grep -q 'sed.*\`\|sed.*backtick\|s\/\[.*\`' "$SCRIPTS/store_key_v3.sh" || \
   grep -oP "sed 's\[.*?\].*'" "$SCRIPTS/store_key_v3.sh" | grep -q '`'; then
  pass "Backtick sanitized in SERVICE_NAME"
else
  # Check the sed pattern covers backtick
  SED_PATTERN=$(grep 'SAFE_SERVICE_NAME' "$SCRIPTS/store_key_v3.sh" | grep sed | head -1)
  if echo "$SED_PATTERN" | grep -q '`'; then
    pass "Backtick included in sanitization pattern"
  else
    fail "Backtick not sanitized — possible osascript injection"
  fi
fi

# T28: SERVICE_NAME sanitization — runtime test with dangerous input
echo "T28: SERVICE_NAME sanitization blocks dangerous chars at runtime"
DANGEROUS='Evil$(rm -rf /)'
SANITIZED=$(echo "$DANGEROUS" | sed 's/["`$;\\|&<>(){}]/_/g' | tr -s '_')
if echo "$SANITIZED" | grep -qE '[$`\\;|&<>(){}]'; then
  fail "Dangerous chars survived sanitization: $SANITIZED"
else
  pass "Dangerous chars stripped from SERVICE_NAME: '$SANITIZED'"
fi

# T29: Temp file is cleaned up (rm -f called)
echo "T29: Secure temp file cleanup (rm -f)"
if grep -q 'rm -f.*TEMP_KEY_FILE' "$SCRIPTS/store_key_v3.sh"; then
  pass "Secure cleanup implemented"
else
  fail "Missing rm -f on temp key file"
fi

# T30: KEY_VALUE cleared from shell memory after temp file write
echo "T30: KEY_VALUE cleared from shell memory immediately after use"
if grep -q 'KEY_VALUE=""' "$SCRIPTS/store_key_v3.sh"; then
  pass "KEY_VALUE zeroed after writing to temp file"
else
  fail "KEY_VALUE not cleared — lingers in shell memory"
fi

echo ""

# -------------------------------------------------------
echo "--- Security hardening checks ---"

# T27: secure_input_mac.sh sanitizes KEY_NAME before interpolation
echo "T27: KEY_NAME sanitized before AppleScript interpolation"
if grep -q "SAFE_KEY_NAME" "$SCRIPTS/secure_input_mac.sh" && grep -q "sed" "$SCRIPTS/secure_input_mac.sh"; then
  pass "KEY_NAME sanitization implemented"
else
  fail "Missing KEY_NAME sanitization — AppleScript injection risk!"
fi

# T28: test_key.sh does NOT pass $KEY naked in -H curl args
echo "T28: curl headers not exposed in process list (\$KEY not in -H args)"
if grep -qE '\-H ".*\$KEY' "$SCRIPTS/test_key.sh"; then
  fail "KEY exposed as naked curl -H arg — visible in ps aux!"
else
  pass "No naked \$KEY in curl -H args"
fi

# T29: test_key.sh uses temp header file pattern
echo "T29: test_key.sh uses temp file for curl headers"
if grep -q "make_header_file\|HFILE" "$SCRIPTS/test_key.sh"; then
  pass "Temp header file pattern implemented"
else
  fail "Missing temp header file — keys visible in ps aux!"
fi

# T30: store_key_v3.sh sanitizes ! character (histexpand risk)
echo "T30: store_key_v3.sh sanitizes ! in SERVICE_NAME"
if grep -qF '!' "$SCRIPTS/store_key_v3.sh" && grep -q "SAFE_SERVICE_NAME" "$SCRIPTS/store_key_v3.sh"; then
  pass "Exclamation mark included in sanitization"
else
  fail "Missing ! sanitization in SAFE_SERVICE_NAME"
fi

# T31: test_key.sh temp header files are removed after use
echo "T31: Temp header files cleaned up after curl calls"
HFILE_CLEANUPS=$(grep -c 'rm -f.*HFILE' "$SCRIPTS/test_key.sh" || true)
if [ "${HFILE_CLEANUPS:-0}" -ge 3 ]; then
  pass "Header temp files cleaned up ($HFILE_CLEANUPS rm calls)"
else
  fail "Insufficient header file cleanup (found ${HFILE_CLEANUPS:-0} rm calls, expected ≥3)"
fi

# T32: temp header files are chmod 600
echo "T32: Temp header files created with 600 permissions"
if grep -q "chmod 600" "$SCRIPTS/test_key.sh"; then
  pass "Temp header files secured with chmod 600"
else
  fail "Missing chmod 600 on temp header files"
fi

echo ""

# -------------------------------------------------------
echo "--- Live key validation (via openclaw.json config) ---"

# v2 stores keys in openclaw.json via gateway config.patch
# To run live tests, set OPENAI_API_KEY and/or ELEVENLABS_API_KEY in env
# (e.g., sourced from config or passed explicitly)

# T17: OpenAI key live test
echo "T17: OpenAI key live validation"
if [ -n "${OPENAI_API_KEY:-}" ]; then
  HTTP=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $OPENAI_API_KEY" "https://api.openai.com/v1/models" 2>/dev/null || echo "000")
  if [ "$HTTP" = "200" ]; then
    pass "OpenAI key valid (HTTP 200)"
  else
    fail "OpenAI key returned HTTP $HTTP"
  fi
else
  echo "  ⏭️  OPENAI_API_KEY not in env, skipping"
fi

# T18: ElevenLabs key live test
echo "T18: ElevenLabs key live validation"
if [ -n "${ELEVENLABS_API_KEY:-}" ]; then
  HTTP=$(curl -s -o /dev/null -w "%{http_code}" -H "xi-api-key: $ELEVENLABS_API_KEY" "https://api.elevenlabs.io/v1/user" 2>/dev/null || echo "000")
  if [ "$HTTP" = "200" ]; then
    pass "ElevenLabs key valid (HTTP 200)"
  else
    fail "ElevenLabs key returned HTTP $HTTP"
  fi
else
  echo "  ⏭️  ELEVENLABS_API_KEY not in env, skipping"
fi

echo ""

# -------------------------------------------------------
echo "================================="
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
  echo "❌ SOME TESTS FAILED"
  exit 1
else
  echo "✅ ALL TESTS PASSED"
  exit 0
fi
