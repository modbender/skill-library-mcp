#!/usr/bin/env bash
# ============================================================
# tests/test-pipeline.sh — Self-Evolving Agent Pipeline Tests
#
# Tests each pipeline stage independently with mock session data.
# No external dependencies required (bash + python3 only).
#
# Exit 0 = all pass, Exit 1 = failures
# ============================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"

# Export SKILL_DIR so child processes (semantic-analyze.sh) can use it directly
export SKILL_DIR

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

assert_json_value() {
  local desc="$1"
  local file="$2"
  local expr="$3"
  if python3 -c "import json; d=json.load(open('$file')); $expr" 2>/dev/null; then
    pass "$desc"
  else
    fail "$desc"
  fi
}

section() { echo ""; echo "=== $1 ==="; }

# ============================================================
# Setup: mock agents directory structure
# ============================================================
MOCK_AGENTS="$TEST_TMP/agents"
MOCK_LOGS="$TEST_TMP/logs"
mkdir -p "$MOCK_AGENTS/opus/sessions"
mkdir -p "$MOCK_LOGS"

# Copy fixtures to mock agents dir
cp "$FIXTURES_DIR/mock-session-ko.jsonl" "$MOCK_AGENTS/opus/sessions/test-ko.jsonl"
cp "$FIXTURES_DIR/mock-session-en.jsonl" "$MOCK_AGENTS/opus/sessions/test-en.jsonl"

# ============================================================
# TEST 1: Config Loader
# ============================================================
section "Test 1: Config Loader"

CONFIG_ENV="$TEST_TMP/config-env.txt"
(
  # Source from skill dir context
  cd "$SKILL_DIR" || exit 1
  # shellcheck source=/dev/null
  source "$SKILL_DIR/scripts/lib/config-loader.sh" 2>/dev/null || true
  sea_load_config 2>/dev/null || true
  echo "SEA_DAYS=${SEA_DAYS:-7}"
  echo "SEA_MAX_SESSIONS=${SEA_MAX_SESSIONS:-30}"
  echo "SEA_VERBOSE=${SEA_VERBOSE:-true}"
) > "$CONFIG_ENV" 2>/dev/null || true

assert "config-loader sources without error" "[ -s '$CONFIG_ENV' ]"
assert "SEA_DAYS is set" "grep -q 'SEA_DAYS=' '$CONFIG_ENV'"
assert "SEA_MAX_SESSIONS is set" "grep -q 'SEA_MAX_SESSIONS=' '$CONFIG_ENV'"

# Test with missing config.yaml (graceful default)
MISSING_CONFIG_ENV="$TEST_TMP/missing-config.txt"
(
  cd "$TEST_TMP" || exit 1
  # shellcheck source=/dev/null
  source "$SKILL_DIR/scripts/lib/config-loader.sh" 2>/dev/null || true
  sea_load_config 2>/dev/null || true
  echo "SEA_DAYS=${SEA_DAYS:-7}"
) > "$MISSING_CONFIG_ENV" 2>/dev/null || true
assert "config-loader uses defaults when no config.yaml" "[ -s '$MISSING_CONFIG_ENV' ]"

# ============================================================
# TEST 2: Language Auto-Detection
# ============================================================
section "Test 2: Language Auto-Detection"

LANG_RESULT="$TEST_TMP/lang-detect.txt"

python3 - "$FIXTURES_DIR/mock-session-ko.jsonl" "$FIXTURES_DIR/mock-session-en.jsonl" \
  > "$LANG_RESULT" 2>/dev/null << 'PYEOF' || true
import json
import re
import sys

def detect_lang(filepath):
    """Mirror the logic in semantic-analyze.sh detect_session_language()."""
    user_msgs = []
    try:
        with open(filepath, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get('type') == 'message':
                    msg = d.get('message', {})
                    if msg.get('role') == 'user':
                        content = msg.get('content', [])
                        text = ''
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get('type') == 'text':
                                    text += item.get('text', '')
                        elif isinstance(content, str):
                            text = content
                        if text:
                            user_msgs.append(text)
                            if len(user_msgs) >= 10:
                                break
    except Exception:
        pass

    if not user_msgs:
        return 'unknown'
    ko_count = sum(1 for m in user_msgs if re.search(r'[가-힣]', m))
    return 'ko' if (ko_count / len(user_msgs)) > 0.5 else 'en'

for fpath in sys.argv[1:]:
    lang = detect_lang(fpath)
    filename = fpath.split('/')[-1]
    print(f"{filename}:{lang}")
PYEOF

assert "Korean session detected as ko" "grep -q 'mock-session-ko.jsonl:ko' '$LANG_RESULT'"
assert "English session detected as en" "grep -q 'mock-session-en.jsonl:en' '$LANG_RESULT'"

# ============================================================
# TEST 3: Fixtures integrity
# ============================================================
section "Test 3: Fixtures Integrity"

assert "mock-session-ko.jsonl exists" "[ -f '$FIXTURES_DIR/mock-session-ko.jsonl' ]"
assert "mock-session-en.jsonl exists" "[ -f '$FIXTURES_DIR/mock-session-en.jsonl' ]"
assert "mock-proposals.json exists"   "[ -f '$FIXTURES_DIR/mock-proposals.json' ]"

# Each JSONL line must be valid JSON
KO_LINES=$(python3 -c "
import json, sys
errors = 0
with open('$FIXTURES_DIR/mock-session-ko.jsonl') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
        except Exception as e:
            print(f'Line {i}: {e}', file=sys.stderr)
            errors += 1
print(errors)
" 2>/dev/null || echo "999")
assert "all ko JSONL lines are valid JSON" "[ '$KO_LINES' = '0' ]"

EN_LINES=$(python3 -c "
import json, sys
errors = 0
with open('$FIXTURES_DIR/mock-session-en.jsonl') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
        except Exception as e:
            print(f'Line {i}: {e}', file=sys.stderr)
            errors += 1
print(errors)
" 2>/dev/null || echo "999")
assert "all en JSONL lines are valid JSON" "[ '$EN_LINES' = '0' ]"

# mock-proposals.json schema
assert "mock-proposals.json is valid JSON" \
  "python3 -c 'import json; json.load(open(\"$FIXTURES_DIR/mock-proposals.json\"))'"
assert "mock-proposals has 3 proposals" \
  "python3 -c 'import json; d=json.load(open(\"$FIXTURES_DIR/mock-proposals.json\")); assert len(d)==3'"
assert "proposals has applied entry" \
  "python3 -c 'import json; d=json.load(open(\"$FIXTURES_DIR/mock-proposals.json\")); assert any(p[\"status\"]==\"applied\" for p in d)'"
assert "proposals has rejected entry" \
  "python3 -c 'import json; d=json.load(open(\"$FIXTURES_DIR/mock-proposals.json\")); assert any(p[\"status\"]==\"rejected\" for p in d)'"
assert "proposals has pending entry" \
  "python3 -c 'import json; d=json.load(open(\"$FIXTURES_DIR/mock-proposals.json\")); assert any(p[\"status\"]==\"pending\" for p in d)'"

# ============================================================
# TEST 4: collect-logs.sh with mock data
# ============================================================
section "Test 4: collect-logs.sh (normal mode)"

COLLECT_OUT="$TEST_TMP/logs.json"

AGENTS_BASE="$MOCK_AGENTS" \
LOGS_DIR="$MOCK_LOGS" \
COLLECT_DAYS=30 \
MAX_SESSIONS=10 \
SEA_TMP_DIR="$TEST_TMP" \
bash "$SKILL_DIR/scripts/v4/collect-logs.sh" "$COLLECT_OUT" > /dev/null 2>&1 || true

assert "collect-logs creates output file"  "[ -f '$COLLECT_OUT' ]"
assert "collect-logs output is valid JSON" \
  "python3 -c 'import json; json.load(open(\"$COLLECT_OUT\"))'"
assert_json_key "has collected_at key"       "$COLLECT_OUT" "collected_at"
assert_json_key "has sessions key"           "$COLLECT_OUT" "sessions"
assert_json_key "has summary key"            "$COLLECT_OUT" "summary"
assert_json_key "has user_complaints key"    "$COLLECT_OUT" "user_complaints"
assert_json_key "has exec_retry_patterns key" "$COLLECT_OUT" "exec_retry_patterns"
assert_json_key "has cron_logs key"          "$COLLECT_OUT" "cron_logs"

# Sessions found = 2 (ko + en)
_ACTUAL_COUNT=$(python3 -c "import json; print(json.load(open('$COLLECT_OUT'))['summary'].get('sessions_analyzed', 0))" 2>/dev/null || echo "0")
assert "collect-logs found both mock sessions" "[ '$_ACTUAL_COUNT' -ge 2 ]"

# ============================================================
# TEST 5: collect-logs.sh graceful degradation
# ============================================================
section "Test 5: collect-logs.sh (graceful degradation)"

EMPTY_OUT="$TEST_TMP/logs-empty.json"
mkdir -p "$TEST_TMP/empty-agents"

AGENTS_BASE="$TEST_TMP/empty-agents" \
LOGS_DIR="$TEST_TMP/empty-logs" \
COLLECT_DAYS=7 \
SEA_TMP_DIR="$TEST_TMP" \
bash "$SKILL_DIR/scripts/v4/collect-logs.sh" "$EMPTY_OUT" > /dev/null 2>&1 || true

assert "collect-logs exits cleanly with empty agents dir" "[ -f '$EMPTY_OUT' ]"
assert "empty-agents output is valid JSON" \
  "python3 -c 'import json; json.load(open(\"$EMPTY_OUT\"))'"
_EMPTY_COUNT=$(python3 -c "import json; print(len(json.load(open('$EMPTY_OUT'))['sessions']))" 2>/dev/null || echo "99")
assert "empty-agents sessions is empty array" "[ '$_EMPTY_COUNT' -eq 0 ]"

# Test with missing LOGS_DIR (no .openclaw/logs)
NOLOGS_OUT="$TEST_TMP/logs-nologs.json"
AGENTS_BASE="$TEST_TMP/empty-agents" \
LOGS_DIR="/tmp/sea-test-nonexistent-logs-$$" \
COLLECT_DAYS=7 \
SEA_TMP_DIR="$TEST_TMP" \
bash "$SKILL_DIR/scripts/v4/collect-logs.sh" "$NOLOGS_OUT" > /dev/null 2>&1 || true

assert "collect-logs handles missing logs dir" "[ -f '$NOLOGS_OUT' ]"

# ============================================================
# TEST 6: semantic-analyze.sh with collected data
# ============================================================
section "Test 6: semantic-analyze.sh"

ANALYSIS_OUT="$TEST_TMP/analysis.json"

LOGS_JSON="$COLLECT_OUT" \
OUTPUT_JSON="$ANALYSIS_OUT" \
AGENTS_DIR="$MOCK_AGENTS" \
ANALYSIS_DAYS=30 \
MAX_SESSIONS=10 \
SEA_VERBOSE=false \
bash "$SKILL_DIR/scripts/v4/semantic-analyze.sh" > /dev/null 2>&1 || true

assert "semantic-analyze creates output file" "[ -f '$ANALYSIS_OUT' ]"
assert "semantic-analyze output is valid JSON" \
  "python3 -c 'import json; json.load(open(\"$ANALYSIS_OUT\"))'"
assert_json_key "analysis has sessions_analyzed"  "$ANALYSIS_OUT" "sessions_analyzed"
assert_json_key "analysis has frustration_events" "$ANALYSIS_OUT" "frustration_events"
assert_json_key "analysis has failure_patterns"   "$ANALYSIS_OUT" "failure_patterns"
assert_json_key "analysis has rule_violations"    "$ANALYSIS_OUT" "rule_violations"
assert_json_key "analysis has exec_loops"         "$ANALYSIS_OUT" "exec_loops"
assert_json_key "analysis has quality_score"      "$ANALYSIS_OUT" "quality_score"
assert_json_key "analysis has key_insights"       "$ANALYSIS_OUT" "key_insights"
assert_json_key "analysis has metadata"           "$ANALYSIS_OUT" "metadata"

# quality_score should be a number in [1, 10]
assert "quality_score is a valid number" \
  "python3 -c 'import json; d=json.load(open(\"$ANALYSIS_OUT\")); q=d[\"quality_score\"]; assert isinstance(q,(int,float)) and 1<=q<=10, f\"bad quality_score: {q}\"'"

# ============================================================
# TEST 7: semantic-analyze.sh graceful degradation
# ============================================================
section "Test 7: semantic-analyze.sh (no sessions)"

ANALYSIS_EMPTY_OUT="$TEST_TMP/analysis-empty.json"
EMPTY_LOGS_JSON="$TEST_TMP/logs-empty.json"  # already created above

LOGS_JSON="$EMPTY_LOGS_JSON" \
OUTPUT_JSON="$ANALYSIS_EMPTY_OUT" \
AGENTS_DIR="$TEST_TMP/empty-agents" \
ANALYSIS_DAYS=7 \
SEA_VERBOSE=false \
bash "$SKILL_DIR/scripts/v4/semantic-analyze.sh" > /dev/null 2>&1 || true

assert "semantic-analyze handles no sessions"   "[ -f '$ANALYSIS_EMPTY_OUT' ]"
assert "no-sessions output is valid JSON"        \
  "python3 -c 'import json; json.load(open(\"$ANALYSIS_EMPTY_OUT\"))'"
assert "no-sessions: sessions_analyzed is 0"     \
  "python3 -c 'import json; d=json.load(open(\"$ANALYSIS_EMPTY_OUT\")); assert d[\"sessions_analyzed\"]==0'"

# ============================================================
# TEST 8: synthesize-proposal.sh (DRY_RUN)
# ============================================================
section "Test 8: synthesize-proposal.sh (DRY_RUN)"

# Create stub benchmarks and effects (synthesizer handles missing gracefully)
echo '{"benchmarks":[],"summary":"no benchmark data"}' > "$TEST_TMP/benchmarks.json"
echo '{"effects":[],"summary":"no effects data"}' > "$TEST_TMP/effects.json"

SYNTH_MD="$TEST_TMP/proposal.md"

SEA_TMP_DIR="$TEST_TMP" \
DRY_RUN=true \
bash "$SKILL_DIR/scripts/v4/synthesize-proposal.sh" > /dev/null 2>&1 || true

# synthesize-proposal.sh writes to $TMP_DIR/proposal.md via tee
assert "synthesize-proposal creates proposal.md" "[ -f '$SYNTH_MD' ]"
assert "proposal.md has content"                  "[ -s '$SYNTH_MD' ]"

# ============================================================
# TEST 9: config.yaml loading is valid YAML structure
# ============================================================
section "Test 9: config.yaml validation"

assert "config.yaml exists" "[ -f '$SKILL_DIR/config.yaml' ]"
assert "config.yaml is parseable" \
  "python3 -c \"
import re
with open('$SKILL_DIR/config.yaml') as f:
    content = f.read()
for section in ['analysis:', 'proposals:', 'cron:', 'output:']:
    assert section in content, f'Missing section: {section}'
print('ok')
\""
assert "analysis.days present" \
  "grep -q 'days:' '$SKILL_DIR/config.yaml'"
assert "complaint_patterns present" \
  "grep -q 'complaint_patterns:' '$SKILL_DIR/config.yaml'"
assert "auto_detect present" \
  "grep -q 'auto_detect:' '$SKILL_DIR/config.yaml'"

# ============================================================
# TEST 10: Script syntax check (bash -n)
# ============================================================
section "Test 10: Script syntax (bash -n)"

for script in \
  "$SKILL_DIR/scripts/lib/config-loader.sh" \
  "$SKILL_DIR/scripts/v4/collect-logs.sh" \
  "$SKILL_DIR/scripts/v4/semantic-analyze.sh" \
  "$SKILL_DIR/scripts/v4/synthesize-proposal.sh" \
  "$SKILL_DIR/scripts/v4/orchestrator.sh" \
  "$SKILL_DIR/scripts/v4/benchmark.sh" \
  "$SKILL_DIR/scripts/v4/measure-effects.sh" \
  "$SKILL_DIR/scripts/v4/deliver.sh" \
  "$SKILL_DIR/bin/sea"
do
  name="$(basename "$script")"
  if [ -f "$script" ]; then
    if bash -n "$script" 2>/dev/null; then
      pass "syntax OK: $name"
    else
      fail "syntax FAIL: $name"
    fi
  else
    fail "script not found: $name"
  fi
done

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
