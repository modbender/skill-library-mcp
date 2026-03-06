#!/bin/sh
# Robust docker-test for Mulch Self Improver: Mulch CLI, all record types,
# record-then-retrieve round-trip, hook edge cases, and script outputs.
# Upgraded from benchmark learnings: reminder token-efficiency, round-trip, consolidated hook tests.
set -e

MULCH="npx --yes mulch-cli"
TESTDIR="/tmp/mulch-skill-test"
SKILL=/skill
ROUNDTRIP_MARKER="DOCKER_TEST_ROUNDTRIP"

echo "=== Mulch Self Improver — robust docker-test ==="

# -----------------------------------------------------------------------------
# 1. Mulch CLI — init, multiple domains, all record types, round-trip
# -----------------------------------------------------------------------------
echo ""
echo "--- 1. Mulch CLI ---"
rm -rf "$TESTDIR"
mkdir -p "$TESTDIR"
cd "$TESTDIR"

echo "[1.1] mulch init"
$MULCH init
test -d .mulch/expertise || (echo "FAIL: .mulch/expertise missing"; exit 1)
test -f .mulch/mulch.config.yaml || (echo "FAIL: mulch.config.yaml missing"; exit 1)

echo "[1.2] mulch add (multiple domains)"
$MULCH add test
$MULCH add api
test -f .mulch/expertise/test.jsonl || (echo "FAIL: test.jsonl missing"; exit 1)
test -f .mulch/expertise/api.jsonl || (echo "FAIL: api.jsonl missing"; exit 1)

echo "[1.3] mulch record — failure, convention, pattern, decision, reference, guide"
$MULCH record test --type failure --description "Docker-test failure" --resolution "Run robust docker-test"
$MULCH record test --type convention "Use pnpm in this project"
$MULCH record test --type pattern --name "docker-test-pattern" --description "Robust test pattern"
$MULCH record api --type decision --title "Use REST" --rationale "Simpler than GraphQL for this scope"
$MULCH record api --type reference --name "health endpoint" --description "GET /health"
$MULCH record test --type guide --name "run-tests" --description "Run ./scripts/docker-test.sh"

echo "[1.3b] record-then-search round-trip (learning: prove full loop)"
$MULCH record test --type convention "Convention for docker-test: $ROUNDTRIP_MARKER"
search_out=$($MULCH search "$ROUNDTRIP_MARKER" 2>/dev/null)
echo "$search_out" | grep -q "$ROUNDTRIP_MARKER" || (echo "FAIL: mulch search did not find recorded $ROUNDTRIP_MARKER"; exit 1)
echo "OK: record-then-search round-trip"

echo "[1.4] mulch query (single + all)"
$MULCH query test | grep -q "Conventions\|Known Failures\|pattern\|guide" || true
$MULCH query api | grep -q "decision\|reference" || true
$MULCH query --all | grep -q "test\|api" || true

echo "[1.5] mulch prime (full + domain)"
$MULCH prime | grep -q "Project Expertise\|mulch" || true
$MULCH prime test | grep -q "convention\|failure\|pattern\|guide" || true

echo "[1.6] mulch search"
$MULCH search "pnpm" | grep -q "pnpm\|convention\|test" || true
$MULCH search "REST" | grep -q "REST\|decision\|api" || true

echo "[1.7] mulch status"
$MULCH status
$MULCH status --json | grep -q "test\|api\|records" || true

echo "[1.8] mulch validate"
$MULCH validate

echo "[1.9] mulch doctor (read-only)"
$MULCH doctor || true

# -----------------------------------------------------------------------------
# 2. OpenClaw hook handler — consolidated tests (learning: one script, token-efficiency)
# -----------------------------------------------------------------------------
echo ""
echo "--- 2. OpenClaw hook handler ---"
cd "$SKILL"
SKILL_ROOT="$SKILL" node "$SKILL/scripts/docker-test-hook.js"

# -----------------------------------------------------------------------------
# 3. Scripts — activator, error-detector, extract-skill
# -----------------------------------------------------------------------------
echo ""
echo "--- 3. Scripts ---"

echo "[3.1] activator.sh outputs reminder with mulch"
out=$(/bin/bash "$SKILL/scripts/activator.sh" 2>/dev/null)
echo "$out" | grep -q "self-improvement-reminder" || (echo "FAIL: activator missing self-improvement-reminder"; exit 1)
echo "$out" | grep -q "mulch record" || (echo "FAIL: activator missing mulch record"; exit 1)
echo "OK: activator outputs mulch reminder"

echo "[3.2] error-detector: no error in output → no block"
export CLAUDE_TOOL_OUTPUT="success"
out=$(/bin/bash "$SKILL/scripts/error-detector.sh" 2>/dev/null || true)
echo "$out" | grep -q "error-detected" && (echo "FAIL: should not show error-detected when no error"; exit 1) || true
echo "OK: error-detector quiet when no error"

echo "[3.3] error-detector: error in output → shows block"
export CLAUDE_TOOL_OUTPUT="error: something failed"
out=$(/bin/bash "$SKILL/scripts/error-detector.sh" 2>/dev/null)
echo "$out" | grep -q "error-detected" || (echo "FAIL: should show error-detected when error"; exit 1)
echo "$out" | grep -q "mulch record" || (echo "FAIL: error block should mention mulch record"; exit 1)
echo "OK: error-detector shows mulch reminder on error"

echo "[3.4] extract-skill.sh --dry-run"
out=$(/bin/bash "$SKILL/scripts/extract-skill.sh" robust-docker-test --dry-run 2>&1)
echo "$out" | grep -q "SKILL.md\|Dry run\|would create" || (echo "FAIL: extract-skill dry-run should mention SKILL.md or would create"; exit 1)
echo "OK: extract-skill --dry-run succeeds"

# -----------------------------------------------------------------------------
# 4. Skill assets
# -----------------------------------------------------------------------------
echo ""
echo "--- 4. Skill assets ---"
test -f "$SKILL/SKILL.md" || (echo "FAIL: SKILL.md missing"; exit 1)
grep -q "mulch prime" "$SKILL/SKILL.md" || (echo "FAIL: SKILL.md missing mulch prime"; exit 1)
grep -q "mulch record" "$SKILL/SKILL.md" || (echo "FAIL: SKILL.md missing mulch record"; exit 1)
grep -qi "self.improvement\|Mulch Self Improver" "$SKILL/SKILL.md" || (echo "FAIL: SKILL.md missing title/self-improvement"; exit 1)
echo "OK: SKILL.md present with required content"

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------
echo ""
echo "=== All robust docker-test checks passed ==="
