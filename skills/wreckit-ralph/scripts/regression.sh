#!/usr/bin/env bash
# wreckit — Regression gate
# Runs full test suite and compares against baseline results
# Usage: ./regression.sh [project-path] [--capture|--compare]
# --capture: save current test results as baseline to .wreckit/regression-baseline.json
# --compare: run tests and diff against saved baseline
# Output: JSON with status PASS/FAIL/WARN

set -euo pipefail
PROJECT="${1:-.}"
MODE="${2:---compare}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

BASELINE_FILE=".wreckit/regression-baseline.json"
CURRENT_FILE=".wreckit/regression-current.json"
RAW_FILE=".wreckit/regression-raw.txt"
mkdir -p .wreckit

STACK_JSON=$($SCRIPT_DIR/detect-stack.sh "$PROJECT" 2>/dev/null || true)
TEST_CMD=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('commands',{}).get('test','none'))" 2>/dev/null || echo "none")
TEST_RUNNER=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('testRunner','none'))" 2>/dev/null || echo "none")

if [ -z "$TEST_CMD" ] || [ "$TEST_CMD" = "none" ]; then
  python3 - <<'PYEOF'
import json
print(json.dumps({
  "status": "WARN",
  "regressions": [],
  "newly_passing": [],
  "total": 0,
  "failed": 0,
  "message": "No test command detected."
}))
PYEOF
  exit 0
fi

RUN_MODE="raw"
CMD="$TEST_CMD"
JSON_FILE=""

case "$TEST_RUNNER" in
  vitest)
    CMD="npx vitest run --reporter=json"
    RUN_MODE="stdout-json"
    ;;
  jest)
    JSON_FILE=".wreckit/jest-results.json"
    CMD="npx jest --json --outputFile=$JSON_FILE"
    RUN_MODE="file-json"
    ;;
  mocha)
    CMD="npx mocha --reporter json"
    RUN_MODE="stdout-json"
    ;;
  pytest)
    JSON_FILE=".wreckit/pytest-report.json"
    CMD="pytest --json-report --json-report-file=$JSON_FILE"
    RUN_MODE="file-json"
    ;;
  go)
    CMD="$TEST_CMD -json"
    RUN_MODE="go-json"
    ;;
  cargo)
    CMD="$TEST_CMD -- --format json"
    RUN_MODE="cargo-json"
    ;;
  node-test)
    CMD="$TEST_CMD -- --test-reporter=json"
    RUN_MODE="stdout-json"
    ;;
  *)
    RUN_MODE="raw"
    ;;
esac

if [ "$RUN_MODE" = "file-json" ] && [ -n "$JSON_FILE" ]; then
  rm -f "$JSON_FILE"
fi

TEST_EXIT=0
set +e
OUTPUT=$(eval "$CMD" 2>&1)
TEST_EXIT=$?
set -e

printf '%s' "$OUTPUT" > "$RAW_FILE"

RUN_JSON=$(python3 - "$RUN_MODE" "$TEST_RUNNER" "$TEST_CMD" "$TEST_EXIT" "$JSON_FILE" "$RAW_FILE" <<'PYEOF'
import json, sys, os

run_mode, test_runner, test_cmd, exit_code, json_file, raw_file = sys.argv[1:]
exit_code = int(exit_code)

with open(raw_file, "r", errors="ignore") as f:
    raw_output = f.read()


def normalize_status(value):
    if value is None:
        return None
    val = str(value).lower()
    if val in {"passed", "pass", "ok", "success"}:
        return "PASS"
    if val in {"failed", "fail", "error"}:
        return "FAIL"
    if val in {"skipped", "pending"}:
        return "SKIP"
    return None


def add_test(results, name, status):
    if not name:
        return
    if status is None:
        return
    results[name] = status


def parse_json_text(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


results = {}

json_text = ""
if run_mode == "file-json" and json_file:
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            json_text = f.read()
    else:
        json_text = ""
else:
    json_text = raw_output

parsed = parse_json_text(json_text)

if run_mode in {"stdout-json", "file-json"} and isinstance(parsed, dict):
    # Jest/Vitest style
    if "testResults" in parsed:
        for suite in parsed.get("testResults", []):
            for assertion in suite.get("assertionResults", []):
                name = assertion.get("fullName") or assertion.get("title")
                status = normalize_status(assertion.get("status"))
                add_test(results, name, status)
    # Mocha style
    if not results and "tests" in parsed and "passes" in parsed:
        pass_set = {t.get("fullTitle") for t in parsed.get("passes", [])}
        fail_set = {t.get("fullTitle") for t in parsed.get("failures", [])}
        for t in parsed.get("tests", []):
            name = t.get("fullTitle")
            if name in fail_set:
                add_test(results, name, "FAIL")
            elif name in pass_set:
                add_test(results, name, "PASS")
    # Pytest json-report
    if not results and "tests" in parsed:
        for t in parsed.get("tests", []):
            name = t.get("nodeid")
            status = normalize_status(t.get("outcome"))
            add_test(results, name, status)

elif run_mode == "go-json":
    for line in raw_output.splitlines():
        try:
            evt = json.loads(line)
        except Exception:
            continue
        action = evt.get("Action")
        name = evt.get("Test")
        if action in {"pass", "fail", "skip"} and name:
            status = "PASS" if action == "pass" else ("FAIL" if action == "fail" else "SKIP")
            add_test(results, name, status)

elif run_mode == "cargo-json":
    for line in raw_output.splitlines():
        try:
            evt = json.loads(line)
        except Exception:
            continue
        if evt.get("type") == "test":
            name = evt.get("name")
            event = evt.get("event")
            status = "PASS" if event in {"ok", "passed"} else ("FAIL" if event in {"failed", "fail"} else None)
            add_test(results, name, status)

# Fallback: single suite test
if not results:
    results = {"suite": "PASS" if exit_code == 0 else "FAIL"}

passed = sum(1 for v in results.values() if v == "PASS")
failed = sum(1 for v in results.values() if v == "FAIL")

run = {
    "testRunner": test_runner,
    "command": test_cmd,
    "summary": {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "exit_code": exit_code,
    },
    "tests": results,
}

print(json.dumps(run))
PYEOF
)

echo "$RUN_JSON" > "$CURRENT_FILE"

if [ "$MODE" = "--capture" ]; then
  echo "$RUN_JSON" > "$BASELINE_FILE"
  STATUS="PASS"
  if [ "$TEST_EXIT" -ne 0 ]; then
    STATUS="FAIL"
  fi
  python3 - "$STATUS" <<'PYEOF'
import json, sys
status = sys.argv[1]
print(json.dumps({
  "status": status,
  "regressions": [],
  "newly_passing": [],
  "total": 0,
  "failed": 0
}))
PYEOF
  exit 0
fi

if [ ! -f "$BASELINE_FILE" ]; then
  python3 - <<'PYEOF'
import json
print(json.dumps({
  "status": "WARN",
  "regressions": [],
  "newly_passing": [],
  "total": 0,
  "failed": 0,
  "message": "No baseline found. Run with --capture first."
}))
PYEOF
  exit 0
fi

COMPARE_JSON=$(python3 - "$BASELINE_FILE" "$CURRENT_FILE" <<'PYEOF'
import json, sys

baseline_file, current_file = sys.argv[1:]

with open(current_file, "r") as f:
    current = json.load(f)
with open(baseline_file, "r") as f:
    baseline = json.load(f)

base_tests = baseline.get("tests", {})
cur_tests = current.get("tests", {})

regressions = []
newly_passing = []

for name, status in base_tests.items():
    cur_status = cur_tests.get(name)
    if status == "PASS" and cur_status != "PASS":
        regressions.append(name)

for name, status in base_tests.items():
    cur_status = cur_tests.get(name)
    if status == "FAIL" and cur_status == "PASS":
        newly_passing.append(name)

failed = sum(1 for v in cur_tests.values() if v == "FAIL")
status = "PASS" if not regressions else "FAIL"

print(json.dumps({
    "status": status,
    "regressions": regressions,
    "newly_passing": newly_passing,
    "total": current.get("summary", {}).get("total", 0),
    "failed": failed
}))
PYEOF
)

echo "$COMPARE_JSON"
