#!/usr/bin/env bash
# wreckit — Full sequential gate runner with telemetry
# Usage: ./run-all-gates.sh [project-path] [mode] [--log-file path]
# Runs ALL gates, collects results, calls proof-bundle.sh
# Tracks timing and validity for every gate

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="${1:-.}"
MODE="${2:-AUDIT}"
LOG_FILE=""

# Optional --log-file
shift 2 || true
while [ $# -gt 0 ]; do
  case "$1" in
    --log-file)
      LOG_FILE="$2"
      shift 2
      ;;
    *)
      shift 1
      ;;
  esac
done

PROJECT="$(cd "$PROJECT" && pwd)"
if [ -z "$LOG_FILE" ]; then
  LOG_FILE=".wreckit/run-$(date +%Y%m%d-%H%M%S).log"
fi

source "$SCRIPT_DIR/telemetry.sh"

TELEMETRY_FILE="$PROJECT/.wreckit/metrics-$(date +%Y%m%d-%H%M%S).json"
export TELEMETRY_FILE

mkdir -p "$PROJECT/.wreckit"

echo "wreckit run: $(date)" | tee -a "$PROJECT/$LOG_FILE"
echo "Project: $PROJECT | Mode: $MODE" | tee -a "$PROJECT/$LOG_FILE"
echo "" | tee -a "$PROJECT/$LOG_FILE"

# Detect project type once (global calibration driver)
PROJECT_TYPE_JSON=$(bash "$SCRIPT_DIR/project-type.sh" "$PROJECT" 2>/dev/null || echo '{}')
if ! echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; json.load(sys.stdin)" >/dev/null 2>&1; then
  PROJECT_TYPE_JSON='{"type":"unknown","confidence":0.0,"signals":["classifier_error"],"calibration":{"slop_per_kloc":5,"god_module_fanin":10,"ci_required":false,"coverage_min":70,"skip_gates":[],"tolerated_warns":[]}}'
fi

echo "$PROJECT_TYPE_JSON" > "$PROJECT/.wreckit/project-type.json"
export WRECKIT_PROJECT_PROFILE_FILE="$PROJECT/.wreckit/project-type.json"

PROJECT_TYPE=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('type','unknown'))" 2>/dev/null || echo "unknown")
PROJECT_TYPE_CONF=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('confidence',0.0))" 2>/dev/null || echo "0.0")
CAL_SLOP_PER_KLOC=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('calibration',{}).get('slop_per_kloc',5))" 2>/dev/null || echo "5")
CAL_GOD_MODULE_FANIN=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('calibration',{}).get('god_module_fanin',10))" 2>/dev/null || echo "10")
CAL_CI_REQUIRED=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(str(bool(d.get('calibration',{}).get('ci_required', False))).lower())" 2>/dev/null || echo "false")
CAL_COVERAGE_MIN=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('calibration',{}).get('coverage_min',70))" 2>/dev/null || echo "70")
CAL_SKIP_GATES=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(','.join(d.get('calibration',{}).get('skip_gates',[])))" 2>/dev/null || echo "")
CAL_TOLERATED_WARNS=$(echo "$PROJECT_TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(','.join(d.get('calibration',{}).get('tolerated_warns',[])))" 2>/dev/null || echo "")

export WRECKIT_PROJECT_TYPE="$PROJECT_TYPE"
export WRECKIT_PROJECT_TYPE_CONFIDENCE="$PROJECT_TYPE_CONF"
export WRECKIT_SLOP_PER_KLOC="$CAL_SLOP_PER_KLOC"
export WRECKIT_GOD_MODULE_FANIN="$CAL_GOD_MODULE_FANIN"
export WRECKIT_CI_REQUIRED="$CAL_CI_REQUIRED"
export WRECKIT_COVERAGE_MIN="$CAL_COVERAGE_MIN"
export WRECKIT_SKIP_GATES="$CAL_SKIP_GATES"
export WRECKIT_TOLERATED_WARNS="$CAL_TOLERATED_WARNS"

echo "Project type: $PROJECT_TYPE (confidence $PROJECT_TYPE_CONF)" | tee -a "$PROJECT/$LOG_FILE"
echo "Calibration: slop_per_kloc=$CAL_SLOP_PER_KLOC god_module_fanin=$CAL_GOD_MODULE_FANIN ci_required=$CAL_CI_REQUIRED coverage_min=$CAL_COVERAGE_MIN" | tee -a "$PROJECT/$LOG_FILE"
if [ -n "$CAL_SKIP_GATES" ]; then
  echo "Profile skip_gates: $CAL_SKIP_GATES" | tee -a "$PROJECT/$LOG_FILE"
fi
echo "" | tee -a "$PROJECT/$LOG_FILE"

# Detect stack once
STACK_JSON=$(bash "$SCRIPT_DIR/detect-stack.sh" "$PROJECT" 2>/dev/null || echo '{}')
TEST_RUNNER=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('testRunner','none'))" 2>/dev/null || echo "none")

# Compute source file count for adaptive timeouts
SOURCE_COUNT=$(find "$PROJECT" \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o -name '*.py' -o -name '*.go' -o -name '*.rs' \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/coverage/*' 2>/dev/null | wc -l | tr -d ' ')
SOURCE_COUNT=${SOURCE_COUNT:-0}

IS_LARGE=0
if [ "$SOURCE_COUNT" -gt 100 ] 2>/dev/null; then
  IS_LARGE=1
fi

SLOP_TIMEOUT=30
DESIGN_TIMEOUT=30
if [ "$IS_LARGE" -eq 1 ]; then
  SLOP_TIMEOUT=60
  DESIGN_TIMEOUT=60
fi

HAS_TIMEOUT=0
if command -v timeout >/dev/null 2>&1; then
  HAS_TIMEOUT=1
fi

GATE_RESULTS="[]"
LAST_GATE_JSON="{}"
BLOCKED_EARLY=0

json_last_from_output() {
  python3 -c 'import json,sys
s=sys.stdin.read()
if not s:
    raise SystemExit(1)
dec=json.JSONDecoder()
last=None
idx=0
while True:
    next_pos=None
    for ch in "{[":
        j=s.find(ch, idx)
        if j!=-1 and (next_pos is None or j<next_pos):
            next_pos=j
    if next_pos is None:
        break
    try:
        obj,end=dec.raw_decode(s[next_pos:])
        last=obj
        idx=next_pos+end
    except Exception:
        idx=next_pos+1
if last is None:
    raise SystemExit(1)
print(json.dumps(last))'
}

append_gate_result() {
  local json_result="$1"
  local merged
  merged=$(python3 -c 'import json,sys; arr=json.loads(sys.argv[1]); arr.append(json.loads(sys.argv[2])); print(json.dumps(arr))' "$GATE_RESULTS" "$json_result" 2>/dev/null || true)
  if [ -n "$merged" ]; then
    GATE_RESULTS="$merged"
  fi
}

replace_last_gate_result() {
  local json_result="$1"
  local merged
  merged=$(python3 -c 'import json,sys; arr=json.loads(sys.argv[1]); item=json.loads(sys.argv[2]); arr[-1:]=[item] if arr else [item]; print(json.dumps(arr))' "$GATE_RESULTS" "$json_result" 2>/dev/null || true)
  if [ -n "$merged" ]; then
    GATE_RESULTS="$merged"
  fi
}

run_and_collect() {
  local gate="$1"
  local script="$2"
  shift 2
  echo "━━━ Running: $gate ━━━" | tee -a "$PROJECT/$LOG_FILE"

  local result
  if [ "$HAS_TIMEOUT" -eq 1 ] && [ -n "${GATE_TIMEOUT:-}" ]; then
    result=$(run_gate "$gate" timeout "${GATE_TIMEOUT}s" bash "$SCRIPT_DIR/$script" "$PROJECT" "$@" 2>&1 | tee -a "$PROJECT/$LOG_FILE")
  else
    result=$(run_gate "$gate" bash "$SCRIPT_DIR/$script" "$PROJECT" "$@" 2>&1 | tee -a "$PROJECT/$LOG_FILE")
  fi

  local json_result
  json_result=$(echo "$result" | json_last_from_output 2>/dev/null || true)

  if [ -z "$json_result" ]; then
    local status="PASS"
    if [ "${LAST_EXIT_CODE:-0}" -ne 0 ]; then
      status="FAIL"
    fi
    json_result=$(python3 -c 'import json,sys; print(json.dumps({"status":sys.argv[1],"gate":sys.argv[2],"raw_output":sys.argv[3][:2000]}))' "$status" "$gate" "$result" 2>/dev/null || echo "{\"status\":\"ERROR\",\"gate\":\"$gate\"}")
  fi

  # Force gate name
  json_result=$(printf '%s' "$json_result" | python3 -c 'import json,sys; d=json.load(sys.stdin); d["gate"]=sys.argv[1]; print(json.dumps(d))' "$gate" 2>/dev/null || echo "{\"gate\":\"$gate\",\"status\":\"ERROR\"}")

  append_gate_result "$json_result"
  LAST_GATE_JSON="$json_result"
  echo "" | tee -a "$PROJECT/$LOG_FILE"

  echo "$json_result"
}

skip_gate() {
  local gate="$1"
  local reason="$2"
  local json_result
  json_result=$(python3 -c "import json; print(json.dumps({'gate':'$gate','status':'SKIP','reason':'$reason'}))")
  append_gate_result "$json_result"
  echo "━━━ Skipping: $gate ━━━" | tee -a "$PROJECT/$LOG_FILE"
  echo "Reason: $reason" | tee -a "$PROJECT/$LOG_FILE"
  echo "" | tee -a "$PROJECT/$LOG_FILE"
}

csv_has_value() {
  local csv="$1"
  local needle="$2"
  [ -z "$csv" ] && return 1
  local entry
  IFS=',' read -r -a _wreckit_csv_values <<< "$csv"
  for entry in "${_wreckit_csv_values[@]}"; do
    entry="$(echo "$entry" | xargs)"
    if [ "$entry" = "$needle" ]; then
      return 0
    fi
  done
  return 1
}

profile_skip_gate_if_needed() {
  local gate="$1"
  if csv_has_value "$CAL_SKIP_GATES" "$gate"; then
    skip_gate "$gate" "project_type_skip:$PROJECT_TYPE"
    return 0
  fi
  return 1
}

apply_tolerance_if_needed() {
  local gate="$1"
  local reason=""
  if csv_has_value "$CAL_TOLERATED_WARNS" "$gate"; then
    reason="tolerated_warn:$gate"
  fi
  if [ "$gate" = "ci_integration" ] && [ "$CAL_CI_REQUIRED" = "false" ]; then
    reason="ci_not_required_for_type:$PROJECT_TYPE"
  fi
  [ -z "$reason" ] && return 0

  local updated
  updated=$(printf '%s' "$LAST_GATE_JSON" | python3 -c 'import json,sys
reason=sys.argv[1]
d=json.load(sys.stdin)
status=str(d.get("status","PASS")).upper()
if status in {"FAIL","ERROR"}:
    d["status"]="WARN"
    d["profile_tolerance"]=reason
print(json.dumps(d))' "$reason" 2>/dev/null || true)

  if [ -n "$updated" ]; then
    LAST_GATE_JSON="$updated"
    replace_last_gate_result "$updated"
  fi
}

# Run detect_stack first
run_and_collect "detect_stack" "detect-stack.sh" >/dev/null

# Early exit helper
check_blocked_and_skip_remaining() {
  if [ "$BLOCKED_EARLY" -eq 1 ]; then
    skip_gate "slop_scan" "early_block"
    skip_gate "type_check" "early_block"
    skip_gate "coverage_stats" "early_block"
    skip_gate "red_team" "early_block"
    skip_gate "regex_complexity" "early_block"
    skip_gate "design_review" "early_block"
    skip_gate "ci_integration" "early_block"
    if [ "$MODE" != "AUDIT" ] || [ -f "$PROJECT/IMPLEMENTATION_PLAN.md" ]; then
      skip_gate "ralph_loop" "early_block"
    fi
    return 0
  fi
  return 1
}

# check_deps
if profile_skip_gate_if_needed "check_deps"; then
  CHECK_DEPS_JSON='{"gate":"check_deps","status":"SKIP"}'
  CHECK_DEPS_BLOCK=0
else
  run_and_collect "check_deps" "check-deps.sh" >/dev/null
  CHECK_DEPS_JSON="$LAST_GATE_JSON"
  apply_tolerance_if_needed "check_deps"
  CHECK_DEPS_JSON="$LAST_GATE_JSON"
  CHECK_DEPS_BLOCK=$(echo "$CHECK_DEPS_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); status=str(d.get('status','PASS')).upper(); conf=float(d.get('confidence',0)); findings=d.get('findings',0); hall=d.get('hallucinated',[]); confirmed=(isinstance(findings,(int,float)) and findings>0) or (isinstance(hall,list) and len(hall)>0); print('1' if status=='FAIL' and conf>=0.9 and confirmed else '0')" 2>/dev/null || echo "0")
  if [ "$CHECK_DEPS_BLOCK" = "1" ]; then
    BLOCKED_EARLY=1
  fi
fi

if check_blocked_and_skip_remaining; then
  summarize_telemetry "$TELEMETRY_FILE" | tee -a "$PROJECT/$LOG_FILE"
  echo "$GATE_RESULTS" | bash "$SCRIPT_DIR/proof-bundle.sh" "$PROJECT" "$MODE" | tee -a "$PROJECT/$LOG_FILE"
  echo ""
  echo "Telemetry: $TELEMETRY_FILE"
  echo "Log: $PROJECT/$LOG_FILE"
  exit 0
fi

# slop_scan
if profile_skip_gate_if_needed "slop_scan"; then
  SLOP_JSON='{"gate":"slop_scan","status":"SKIP"}'
  SLOP_HARD_BLOCK=0
else
  GATE_TIMEOUT="$SLOP_TIMEOUT"
  run_and_collect "slop_scan" "slop-scan.sh" >/dev/null
  SLOP_JSON="$LAST_GATE_JSON"
  unset GATE_TIMEOUT
  apply_tolerance_if_needed "slop_scan"
  SLOP_JSON="$LAST_GATE_JSON"
  SLOP_COUNT=$(echo "$SLOP_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('actionable_findings',0))" 2>/dev/null || echo "")
  SLOP_HARD_BLOCK=$(echo "$SLOP_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); status=str(d.get('status','PASS')).upper(); fd=d.get('density_per_kloc'); md=d.get('threshold_per_kloc'); print('1' if status=='FAIL' and isinstance(fd,(int,float)) and isinstance(md,(int,float)) and md>0 and fd>(3*md) else '0')" 2>/dev/null || echo "0")
  if [ "$SLOP_HARD_BLOCK" = "1" ]; then
    BLOCKED_EARLY=1
  fi
fi

if check_blocked_and_skip_remaining; then
  summarize_telemetry "$TELEMETRY_FILE" | tee -a "$PROJECT/$LOG_FILE"
  echo "$GATE_RESULTS" | bash "$SCRIPT_DIR/proof-bundle.sh" "$PROJECT" "$MODE" | tee -a "$PROJECT/$LOG_FILE"
  echo ""
  echo "Telemetry: $TELEMETRY_FILE"
  echo "Log: $PROJECT/$LOG_FILE"
  exit 0
fi

# type_check
if profile_skip_gate_if_needed "type_check"; then
  TYPE_JSON='{"gate":"type_check","status":"SKIP"}'
  TYPE_HARD_BLOCK=0
else
  run_and_collect "type_check" "type-check.sh" >/dev/null
  TYPE_JSON="$LAST_GATE_JSON"
  apply_tolerance_if_needed "type_check"
  TYPE_JSON="$LAST_GATE_JSON"
  TYPE_ERRORS=$(echo "$TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('errors',0))" 2>/dev/null || echo 0)
  TYPE_HARD_BLOCK=$(echo "$TYPE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); status=str(d.get('status','PASS')).upper(); errors=int(d.get('errors',0)); print('1' if status=='FAIL' and errors>0 else '0')" 2>/dev/null || echo "0")
  if [ "$TYPE_HARD_BLOCK" = "1" ]; then
    BLOCKED_EARLY=1
  fi
fi

if check_blocked_and_skip_remaining; then
  summarize_telemetry "$TELEMETRY_FILE" | tee -a "$PROJECT/$LOG_FILE"
  echo "$GATE_RESULTS" | bash "$SCRIPT_DIR/proof-bundle.sh" "$PROJECT" "$MODE" | tee -a "$PROJECT/$LOG_FILE"
  echo ""
  echo "Telemetry: $TELEMETRY_FILE"
  echo "Log: $PROJECT/$LOG_FILE"
  exit 0
fi

# coverage_stats (skip if no tests)
if profile_skip_gate_if_needed "coverage_stats"; then
  :
elif [ "$TEST_RUNNER" = "none" ] || [ -z "$TEST_RUNNER" ]; then
  skip_gate "coverage_stats" "no_test_runner"
else
  run_and_collect "coverage_stats" "coverage-stats.sh" >/dev/null
  apply_tolerance_if_needed "coverage_stats"
fi

# red_team
if profile_skip_gate_if_needed "red_team"; then
  :
else
  run_and_collect "red_team" "red-team.sh" >/dev/null
  apply_tolerance_if_needed "red_team"
fi

# regex_complexity (optional)
if profile_skip_gate_if_needed "regex_complexity"; then
  :
else
  REGEX_COUNT=$( (grep -rE "RegExp|/.+/" "$PROJECT/src" 2>/dev/null || true) | wc -l | tr -d ' ' )
  REGEX_COUNT=${REGEX_COUNT:-0}
  if [ "$REGEX_COUNT" -gt 20 ]; then
    run_and_collect "regex_complexity" "regex-complexity.sh" "$PROJECT" >/dev/null
    apply_tolerance_if_needed "regex_complexity"
  else
    skip_gate "regex_complexity" "low_regex_density"
  fi
fi

# design_review (double timeout for large projects)
if profile_skip_gate_if_needed "design_review"; then
  :
else
  GATE_TIMEOUT="$DESIGN_TIMEOUT"
  run_and_collect "design_review" "design-review.sh" >/dev/null
  unset GATE_TIMEOUT
  apply_tolerance_if_needed "design_review"
fi

# ci_integration (profile may tolerate WARN)
if profile_skip_gate_if_needed "ci_integration"; then
  CI_JSON='{"gate":"ci_integration","status":"SKIP"}'
  CI_FOUND="false"
else
  run_and_collect "ci_integration" "ci-integration.sh" >/dev/null
  apply_tolerance_if_needed "ci_integration"
  CI_JSON="$LAST_GATE_JSON"
  CI_FOUND=$(echo "$CI_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('ci_found', True))" 2>/dev/null || echo "true")
fi

# ralph_loop
if profile_skip_gate_if_needed "ralph_loop"; then
  :
elif [ "$MODE" = "AUDIT" ] && [ ! -f "$PROJECT/IMPLEMENTATION_PLAN.md" ]; then
  skip_gate "ralph_loop" "audit_no_plan"
elif [ "$MODE" != "AUDIT" ] || [ -f "$PROJECT/IMPLEMENTATION_PLAN.md" ]; then
  run_and_collect "ralph_loop" "ralph-loop.sh" >/dev/null
  apply_tolerance_if_needed "ralph_loop"
fi

# Print telemetry summary
summarize_telemetry "$TELEMETRY_FILE" | tee -a "$PROJECT/$LOG_FILE"

# Write proof bundle
echo "$GATE_RESULTS" | bash "$SCRIPT_DIR/proof-bundle.sh" "$PROJECT" "$MODE" | tee -a "$PROJECT/$LOG_FILE"

echo ""
echo "Telemetry: $TELEMETRY_FILE"
echo "Log: $PROJECT/$LOG_FILE"
