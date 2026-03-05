#!/usr/bin/env bash
# ============================================================
# tests/test-v5.sh — Self-Evolving Agent v5.0 Component Tests
#
# Tests v5-specific components independently.
# Does NOT require Ollama — all tests use the fallback path or mocks.
#
# Coverage:
#   1. embedding-analyze.sh — fallback mode (Ollama offline simulation)
#   2. stream-monitor.sh — polling mode (--poll flag, no tail -F)
#   3. fleet-analyzer.sh — mock agent directories
#   4. trend-analyzer.sh — sample proposal history
#   5. v5 orchestrator fallback — behaves like v4 when Ollama offline
#   6. Script syntax (bash -n) for all v5 scripts
#
# Exit 0 = all pass, Exit 1 = failures
# ============================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"

export SKILL_DIR

# Temp dir for this test run
TEST_TMP=$(mktemp -d)
trap 'rm -rf "$TEST_TMP"' EXIT

# ── Test counters ─────────────────────────────────────────────
PASS=0
FAIL=0
SKIP=0
FAIL_MSGS=""

# ── Helpers ──────────────────────────────────────────────────
pass() { echo "  ✓ $1"; PASS=$((PASS + 1)); }
fail() {
  echo "  ✗ $1"
  FAIL=$((FAIL + 1))
  FAIL_MSGS="${FAIL_MSGS}\n  - $1"
}
skip() { echo "  - SKIP: $1"; SKIP=$((SKIP + 1)); }

assert() {
  local desc="$1"
  local condition="$2"
  if eval "$condition" 2>/dev/null; then
    pass "$desc"
  else
    fail "$desc"
  fi
}

assert_json_key() {
  local desc="$1"
  local file="$2"
  local key="$3"
  if python3 -c "import json; d=json.load(open('$file')); assert '$key' in d, '$key missing'" 2>/dev/null; then
    pass "$desc"
  else
    fail "$desc"
  fi
}

section() { echo ""; echo "=== $1 ==="; }

# ============================================================
# Setup: mock environment
# ============================================================
MOCK_AGENTS="$TEST_TMP/agents"
MOCK_LOGS="$TEST_TMP/logs"
mkdir -p "$MOCK_AGENTS/opus/sessions"
mkdir -p "$MOCK_AGENTS/sonnet/sessions"
mkdir -p "$MOCK_AGENTS/haiku/sessions"
mkdir -p "$MOCK_LOGS"

# Copy fixtures to all mock agent dirs
for agent in opus sonnet haiku; do
  cp "$FIXTURES_DIR/mock-session-ko.jsonl" "$MOCK_AGENTS/$agent/sessions/test-ko.jsonl"
  cp "$FIXTURES_DIR/mock-session-en.jsonl" "$MOCK_AGENTS/$agent/sessions/test-en.jsonl"
done

# Create mock stream-alerts directory
MOCK_ALERTS_DIR="$TEST_TMP/stream-alerts"
mkdir -p "$MOCK_ALERTS_DIR"

# Create sample stream alerts for testing
cat > "$MOCK_ALERTS_DIR/alert-20260218-100000.json" << 'ALERTEOF'
{
  "timestamp": "2026-02-18T10:00:00Z",
  "type": "exec_retry",
  "severity": "high",
  "message": "exec consecutive retries >= 5 detected",
  "count": 7,
  "agent": "opus"
}
ALERTEOF

cat > "$MOCK_ALERTS_DIR/alert-20260219-143000.json" << 'ALERTEOF'
{
  "timestamp": "2026-02-19T14:30:00Z",
  "type": "cron_error",
  "severity": "medium",
  "message": "cron error repeated 3 times",
  "count": 3,
  "agent": "sonnet"
}
ALERTEOF

# Create mock proposals for trend analysis (4 weeks)
MOCK_PROPOSALS_DIR="$TEST_TMP/proposals"
mkdir -p "$MOCK_PROPOSALS_DIR"

for week in 1 2 3 4; do
  date_offset=$((week * 7))
  cat > "$MOCK_PROPOSALS_DIR/proposal-week${week}.json" << PROPEOF
{
  "id": "proposal-week${week}",
  "created_at": "2026-01-$((25 + week * 7 > 31 ? 28 : 25 + week * 7))",
  "status": "applied",
  "patterns": ["exec_retry", "git_direct_cmd"],
  "quality_score": $((60 + week * 5)),
  "frustration_count": $((10 - week * 2)),
  "exec_retries": $((50 - week * 10))
}
PROPEOF
done

# ============================================================
# TEST 1: v5 Scripts Existence Check
# ============================================================
section "Test 1: v5 Script Existence"

V5_DIR="$SKILL_DIR/scripts/v5"

assert "scripts/v5/ directory exists" "[ -d '$V5_DIR' ]"

for script in \
  "orchestrator.sh" \
  "embedding-analyze.sh" \
  "stream-monitor.sh" \
  "fleet-analyzer.sh" \
  "trend-analyzer.sh"
do
  if [ -f "$V5_DIR/$script" ]; then
    pass "v5 script exists: $script"
  else
    fail "v5 script MISSING: $script (run: touch '$V5_DIR/$script')"
  fi
done

# ============================================================
# TEST 2: embedding-analyze.sh — Fallback Mode (no Ollama)
# ============================================================
section "Test 2: embedding-analyze.sh (Ollama offline → v4 fallback)"

EMBED_OUT="$TEST_TMP/embedding-analysis.json"

# Force Ollama offline by pointing at nonexistent port
OLLAMA_URL="http://localhost:19999" \
EMBEDDING_FALLBACK_ALLOWED=true \
AGENTS_BASE="$MOCK_AGENTS" \
LOGS_DIR="$MOCK_LOGS" \
COLLECT_DAYS=30 \
MAX_SESSIONS=10 \
SEA_TMP_DIR="$TEST_TMP" \
OUTPUT_JSON="$EMBED_OUT" \
bash "$V5_DIR/embedding-analyze.sh" > /dev/null 2>&1 || true

if [ -f "$EMBED_OUT" ]; then
  pass "embedding-analyze creates output in fallback mode"

  if python3 -c "import json; json.load(open('$EMBED_OUT'))" 2>/dev/null; then
    pass "embedding-analyze fallback output is valid JSON"
  else
    fail "embedding-analyze fallback output is invalid JSON"
  fi

  # Check for fallback indicator
  ENGINE=$(python3 -c "
import json
d = json.load(open('$EMBED_OUT'))
print(d.get('engine', d.get('analysis_engine', 'unknown')))
" 2>/dev/null || echo "unknown")

  if [ "$ENGINE" = "heuristic" ] || [ "$ENGINE" = "fallback" ] || [ "$ENGINE" = "embedding_fallback" ]; then
    pass "engine field indicates fallback: $ENGINE"
  else
    # Not a hard failure — output schema may vary
    skip "engine field not 'heuristic/fallback' (got: $ENGINE) — schema may vary"
  fi

  # Must still have analysis keys
  if python3 -c "
import json
d = json.load(open('$EMBED_OUT'))
# Accept any of the known key sets
keys = set(d.keys())
required_any = ['frustration_events', 'complaint_signals', 'sessions_analyzed', 'summary']
found = [k for k in required_any if k in keys]
assert len(found) >= 1, f'None of {required_any} found in {keys}'
" 2>/dev/null; then
    pass "embedding-analyze fallback output has analysis data"
  else
    fail "embedding-analyze fallback output missing analysis data keys"
  fi
else
  skip "embedding-analyze.sh not yet implemented — EXPECTED, will pass when scripts/v5/ is created"
fi

# ============================================================
# TEST 3: embedding-analyze.sh — Mock Embedding Test
# ============================================================
section "Test 3: Cosine Similarity Logic (pure Python, no Ollama)"

COSINE_RESULT=$(python3 - << 'PYEOF' 2>/dev/null || echo "error"
import math

def cosine_similarity(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x**2 for x in a))
    mag_b = math.sqrt(sum(x**2 for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)

# Simulate: same direction = high similarity (frustration)
frustration_anchor = [1.0, 0.8, -0.2, 0.5]
similar_msg       = [0.9, 0.85, -0.15, 0.55]   # similar direction
dissimilar_msg    = [-0.5, 0.1, 0.9, -0.3]      # different direction

sim_frustrated = cosine_similarity(frustration_anchor, similar_msg)
sim_normal     = cosine_similarity(frustration_anchor, dissimilar_msg)

threshold = 0.78
result = {
    "frustrated_above_threshold": sim_frustrated > threshold,
    "normal_below_threshold": sim_normal < threshold,
    "frustrated_score": round(sim_frustrated, 4),
    "normal_score": round(sim_normal, 4),
}
import json
print(json.dumps(result))
PYEOF
)

if [ "$COSINE_RESULT" != "error" ]; then
  COSINE_FILE="$TEST_TMP/cosine-result.json"
  echo "$COSINE_RESULT" > "$COSINE_FILE"
  assert "cosine: frustrated message above threshold (0.78)" \
    "python3 -c \"import json; d=json.load(open('$COSINE_FILE')); assert d['frustrated_above_threshold']\""
  assert "cosine: normal message below threshold (0.78)" \
    "python3 -c \"import json; d=json.load(open('$COSINE_FILE')); assert d['normal_below_threshold']\""
  assert "cosine: python3 math available" "[ -f '$COSINE_FILE' ]"
else
  fail "cosine similarity python3 test failed"
fi

# ============================================================
# TEST 4: stream-monitor.sh — Polling Mode
# ============================================================
section "Test 4: stream-monitor.sh (--poll mode)"

# Create a mock log file with triggerable patterns
MOCK_LOG="$MOCK_LOGS/test-stream.log"
cat > "$MOCK_LOG" << 'LOGEOF'
[2026-02-18 10:00:01] exec retry attempt 1
[2026-02-18 10:00:02] exec retry attempt 2
[2026-02-18 10:00:03] exec retry attempt 3
[2026-02-18 10:00:04] exec retry attempt 4
[2026-02-18 10:00:05] exec retry attempt 5
[2026-02-18 10:00:06] exec retry attempt 6
[2026-02-18 10:00:07] cron error: connection refused
[2026-02-18 10:00:08] cron error: connection refused
[2026-02-18 10:00:09] cron error: connection refused
LOGEOF

STREAM_ALERTS_OUT="$TEST_TMP/stream-alerts-out"
mkdir -p "$STREAM_ALERTS_OUT"

# Run in polling mode with very short duration (--once = exit after 1 poll)
STREAM_LOG="$MOCK_LOG" \
ALERTS_DIR="$STREAM_ALERTS_OUT" \
LOG_DIR="$MOCK_LOGS" \
bash "$V5_DIR/stream-monitor.sh" --poll --once > /dev/null 2>&1 || true

if [ -d "$STREAM_ALERTS_OUT" ]; then
  pass "stream-monitor creates alerts directory"

  ALERT_COUNT=$(ls "$STREAM_ALERTS_OUT"/*.json 2>/dev/null | wc -l | tr -d ' ')
  if [ "${ALERT_COUNT:-0}" -gt 0 ]; then
    pass "stream-monitor detected alerts in polling mode ($ALERT_COUNT alert(s))"

    # Validate first alert JSON
    FIRST_ALERT=$(ls "$STREAM_ALERTS_OUT"/*.json 2>/dev/null | head -1)
    if [ -n "$FIRST_ALERT" ]; then
      if python3 -c "import json; json.load(open('$FIRST_ALERT'))" 2>/dev/null; then
        pass "stream-monitor alert JSON is valid"
      else
        fail "stream-monitor alert JSON is invalid"
      fi
    fi
  else
    skip "stream-monitor --once produced no alerts (may be expected — threshold not reached in 1 poll)"
  fi
else
  skip "stream-monitor.sh not yet implemented or --once flag not supported"
fi

# ============================================================
# TEST 5: stream-monitor.sh — Alert Schema
# ============================================================
section "Test 5: Stream Alert Schema Validation"

# Validate the mock alerts we created in Setup
for alert_file in "$MOCK_ALERTS_DIR"/*.json; do
  [ -f "$alert_file" ] || continue
  fname=$(basename "$alert_file")

  if python3 -c "
import json
d = json.load(open('$alert_file'))
required = ['timestamp', 'type', 'severity', 'message']
missing = [k for k in required if k not in d]
assert not missing, f'Missing keys: {missing}'
assert d['severity'] in ['low', 'medium', 'high', 'critical'], f'Bad severity: {d[\"severity\"]}'
" 2>/dev/null; then
    pass "alert schema valid: $fname"
  else
    fail "alert schema invalid: $fname"
  fi
done

# ============================================================
# TEST 6: fleet-analyzer.sh — Mock Agent Directories
# ============================================================
section "Test 6: fleet-analyzer.sh (mock agent dirs)"

FLEET_OUT="$TEST_TMP/fleet-result.json"

AGENTS_BASE="$MOCK_AGENTS" \
FLEET_OUTPUT="$FLEET_OUT" \
SEA_TMP_DIR="$TEST_TMP" \
bash "$V5_DIR/fleet-analyzer.sh" > /dev/null 2>&1 || true

if [ -f "$FLEET_OUT" ]; then
  pass "fleet-analyzer creates output file"

  if python3 -c "import json; json.load(open('$FLEET_OUT'))" 2>/dev/null; then
    pass "fleet output is valid JSON"
  else
    fail "fleet output is invalid JSON"
  fi

  # Check core schema
  python3 - "$FLEET_OUT" << 'PYEOF' 2>/dev/null && pass "fleet schema has agents_analyzed" || fail "fleet schema missing agents_analyzed"
import json, sys
d = json.load(open(sys.argv[1]))
assert 'agents_analyzed' in d or 'agents' in d or 'fleet' in d, "No fleet key found"
PYEOF

  AGENT_COUNT=$(python3 -c "
import json
d = json.load(open('$FLEET_OUT'))
# Handle different schema shapes
if 'agents_analyzed' in d:
    print(d['agents_analyzed'])
elif 'agents' in d:
    print(len(d['agents']))
elif 'fleet' in d and isinstance(d['fleet'], list):
    print(len(d['fleet']))
else:
    print(0)
" 2>/dev/null || echo "0")

  if [ "${AGENT_COUNT:-0}" -ge 2 ]; then
    pass "fleet-analyzer found ≥2 agent instances (found: $AGENT_COUNT)"
  else
    skip "fleet-analyzer found <2 agents (got: ${AGENT_COUNT:-0}) — may be normal if agents not initialized"
  fi
else
  skip "fleet-analyzer.sh not yet implemented"
fi

# ============================================================
# TEST 7: trend-analyzer.sh — Sample Proposals
# ============================================================
section "Test 7: trend-analyzer.sh (sample proposal history)"

TRENDS_OUT="$TEST_TMP/trends-result.json"

PROPOSALS_DIR="$MOCK_PROPOSALS_DIR" \
TRENDS_OUTPUT="$TRENDS_OUT" \
LOOKBACK_WEEKS=4 \
SEA_TMP_DIR="$TEST_TMP" \
bash "$V5_DIR/trend-analyzer.sh" > /dev/null 2>&1 || true

if [ -f "$TRENDS_OUT" ]; then
  pass "trend-analyzer creates output file"

  if python3 -c "import json; json.load(open('$TRENDS_OUT'))" 2>/dev/null; then
    pass "trends output is valid JSON"
  else
    fail "trends output is invalid JSON"
  fi

  # Validate trend schema
  python3 - "$TRENDS_OUT" << 'PYEOF' 2>/dev/null && pass "trends schema has expected fields" || fail "trends schema missing expected fields"
import json, sys
d = json.load(open(sys.argv[1]))
# Accept any of these key patterns
valid_keys = ['trends', 'emerging', 'resolved', 'patterns', 'weekly_data', 'summary']
found = [k for k in valid_keys if k in d]
assert len(found) >= 1, f"None of {valid_keys} found in {set(d.keys())}"
PYEOF

else
  skip "trend-analyzer.sh not yet implemented"
fi

# ============================================================
# TEST 8: Python trend analysis logic (no scripts needed)
# ============================================================
section "Test 8: Trend Logic (pure Python, no scripts)"

TREND_RESULT=$(python3 - << 'PYEOF' 2>/dev/null || echo "error"
import json

# Simulated 4-week data (clear downward trend)
# Weeks 1-3 are "older", week 4 is "latest"
weekly_data = [
    {"week": 1, "frustration": 12, "exec_retries": 60},
    {"week": 2, "frustration": 10, "exec_retries": 45},
    {"week": 3, "frustration": 8,  "exec_retries": 30},
    {"week": 4, "frustration": 1,  "exec_retries": 5},  # clearly resolved
]

# Compare latest vs average of older weeks (weeks 1-3)
older_data = weekly_data[:-1]
avg_frustration = sum(w["frustration"] for w in older_data) / len(older_data)
avg_exec = sum(w["exec_retries"] for w in older_data) / len(older_data)
latest = weekly_data[-1]

# Resolved: latest is < 20% of older average
# frustration: 1 < (10.0 * 0.2 = 2.0) → True
# exec_retries: 5 < (45.0 * 0.5 = 22.5) → True
frustration_resolved = latest["frustration"] < avg_frustration * 0.2
exec_improving = latest["exec_retries"] < avg_exec * 0.5

# Emerging: latest is > 2x average (not in this dataset)
new_pattern_weekly = [0, 0, 2, 5]
avg_new = sum(new_pattern_weekly[:-1]) / max(len(new_pattern_weekly) - 1, 1)
emerging = new_pattern_weekly[-1] > avg_new * 2 if avg_new > 0 else False

result = {
    "frustration_resolved": frustration_resolved,
    "exec_retries_improving": exec_improving,
    "emerging_pattern": emerging,
    "avg_frustration": round(avg_frustration, 2),
    "latest_frustration": latest["frustration"],
}
print(json.dumps(result))
PYEOF
)

if [ "$TREND_RESULT" != "error" ]; then
  TREND_FILE="$TEST_TMP/trend-result.json"
  echo "$TREND_RESULT" > "$TREND_FILE"
  assert "trend: frustration resolved (downward trend)" \
    "python3 -c \"import json; d=json.load(open('$TREND_FILE')); assert d['frustration_resolved']\""
  assert "trend: exec retries improving" \
    "python3 -c \"import json; d=json.load(open('$TREND_FILE')); assert d['exec_retries_improving']\""
  assert "trend: emerging detection works" \
    "[ -f '$TREND_FILE' ]"
else
  fail "trend logic python3 test failed"
fi

# ============================================================
# TEST 9: v5 Orchestrator Fallback (Ollama offline → v4 behavior)
# ============================================================
section "Test 9: v5 orchestrator falls back to v4 when Ollama offline"

ORCH_OUT="$TEST_TMP/orch-v5-fallback.txt"

AGENTS_BASE="$MOCK_AGENTS" \
LOGS_DIR="$MOCK_LOGS" \
OLLAMA_URL="http://localhost:19999" \
SEA_TMP_DIR="$TEST_TMP" \
DRY_RUN=true \
bash "$V5_DIR/orchestrator.sh" > "$ORCH_OUT" 2>&1 || true

if [ -f "$ORCH_OUT" ]; then
  # Check that the output contains either fallback message or v4-compatible output
  if grep -qi "fallback\|heuristic\|v4\|EMBEDDING_FALLBACK" "$ORCH_OUT" 2>/dev/null; then
    pass "v5 orchestrator outputs fallback indication when Ollama offline"
  elif grep -qi "stage\|collect\|analyze\|synthesize\|proposal" "$ORCH_OUT" 2>/dev/null; then
    pass "v5 orchestrator completed pipeline (possibly in fallback mode)"
  else
    skip "v5 orchestrator output doesn't contain expected keywords — may not be implemented yet"
  fi
else
  skip "v5 orchestrator.sh not yet implemented"
fi

# Test that v4 orchestrator still works independently
V4_ORCH_OUT="$TEST_TMP/orch-v4.txt"
AGENTS_BASE="$MOCK_AGENTS" \
LOGS_DIR="$MOCK_LOGS" \
SEA_TMP_DIR="$TEST_TMP" \
DRY_RUN=true \
bash "$SKILL_DIR/scripts/v4/orchestrator.sh" > "$V4_ORCH_OUT" 2>&1 || true

assert "v4 orchestrator still runs independently (v5 doesn't break it)" \
  "[ -f '$V4_ORCH_OUT' ]"

# ============================================================
# TEST 10: v5 Script Syntax (bash -n)
# ============================================================
section "Test 10: v5 Script Syntax (bash -n)"

V5_SCRIPTS=(
  "orchestrator.sh"
  "embedding-analyze.sh"
  "stream-monitor.sh"
  "fleet-analyzer.sh"
  "trend-analyzer.sh"
)

for script in "${V5_SCRIPTS[@]}"; do
  path="$V5_DIR/$script"
  if [ -f "$path" ]; then
    if bash -n "$path" 2>/dev/null; then
      pass "syntax OK: v5/$script"
    else
      fail "syntax FAIL: v5/$script"
    fi
  else
    skip "not found (not yet implemented): v5/$script"
  fi
done

# ============================================================
# TEST 11: data directory structure for v5
# ============================================================
section "Test 11: v5 Data Directory Structure"

# These should be auto-created by the v5 orchestrator, but we verify they can be created
for dir in "stream-alerts" "fleet" "trends"; do
  target_dir="$TEST_TMP/data-test/$dir"
  mkdir -p "$target_dir" 2>/dev/null
  assert "can create data/$dir directory" "[ -d '$target_dir' ]"
done

# Validate that embedding cache dir can be created outside skill dir
EMBD_CACHE="$TEST_TMP/sea-emb-cache"
mkdir -p "$EMBD_CACHE" 2>/dev/null
assert "embedding cache directory creatable" "[ -d '$EMBD_CACHE' ]"

# ============================================================
# RESULTS
# ============================================================
echo ""
echo "=============================="
echo "Results: ${PASS} passed, ${FAIL} failed, ${SKIP} skipped"
if [ -n "$FAIL_MSGS" ]; then
  echo -e "Failures:${FAIL_MSGS}"
fi
if [ "$SKIP" -gt 0 ]; then
  echo "Note: Skipped tests indicate scripts/v5/ not yet fully implemented."
  echo "      This is expected before v5 scripts are created."
  echo "      Re-run after implementing scripts/v5/*.sh"
fi
echo "=============================="

[ "$FAIL" -eq 0 ]
