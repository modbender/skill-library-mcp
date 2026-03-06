#!/usr/bin/env bash
# wreckit — extract raw coverage stats from test runners
# Usage: ./coverage-stats.sh [project-path]
# Outputs JSON with coverage numbers
# Fix: use absolute script path for detect-stack (works from any cwd)

set -euo pipefail
PROJECT="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

# Detect stack
STACK=$(bash "$SCRIPT_DIR/detect-stack.sh" "$PROJECT" 2>/dev/null)
LANG=$(echo "$STACK" | python3 -c "import sys,json; print(json.load(sys.stdin).get('language','unknown'))" 2>/dev/null || echo "unknown")
TEST_RUNNER=$(echo "$STACK" | python3 -c "import sys,json; print(json.load(sys.stdin).get('testRunner','none'))" 2>/dev/null || echo "none")

case "$TEST_RUNNER" in
  vitest)
    # vitest writes coverage to coverage/coverage-summary.json (not stdout)
    npx vitest run --coverage --coverage.reporter=json-summary >/dev/null 2>&1 || true
    if [ -f "coverage/coverage-summary.json" ]; then
      cat coverage/coverage-summary.json
    elif [ -f "coverage/coverage-final.json" ]; then
      # Summarize from final coverage file
      python3 -c "
import json
with open('coverage/coverage-final.json') as f:
    data = json.load(f)
total_stmts = sum(len(v.get('s',{})) for v in data.values())
covered = sum(1 for v in data.values() for c in v.get('s',{}).values() if c > 0)
pct = round(covered * 100 / total_stmts, 1) if total_stmts > 0 else 0
print(json.dumps({'total': {'statements': {'pct': pct, 'total': total_stmts, 'covered': covered}}}))
" 2>/dev/null || echo '{"error":"could not parse vitest coverage"}'
    else
      echo '{"error":"vitest coverage file not found — ensure @vitest/coverage-v8 or @vitest/coverage-istanbul is installed"}'
    fi
    ;;
  jest)
    npx jest --coverage --coverageReporters=json-summary >/dev/null 2>&1
    if [ -f "coverage/coverage-summary.json" ]; then
      cat coverage/coverage-summary.json
    else
      echo '{"error":"jest coverage file not found"}'
    fi
    ;;
  pytest)
    pytest --cov=. --cov-report=json >/dev/null 2>&1
    if [ -f "coverage.json" ]; then
      cat coverage.json
    else
      echo '{"error":"pytest coverage file not found"}'
    fi
    ;;
  cargo)
    # cargo-tarpaulin for Rust coverage
    if command -v cargo-tarpaulin &>/dev/null; then
      cargo tarpaulin --out Json 2>/dev/null || echo '{"error":"tarpaulin failed"}'
    else
      echo '{"error":"cargo-tarpaulin not installed","hint":"cargo install cargo-tarpaulin"}'
    fi
    ;;
  go)
    go test -coverprofile=coverage.out ./... >/dev/null 2>&1
    if [ -f "coverage.out" ]; then
      go tool cover -func=coverage.out | tail -1
      rm -f coverage.out
    else
      echo '{"error":"go coverage failed"}'
    fi
    ;;
  swift)
    swift test --enable-code-coverage 2>/dev/null || echo '{"error":"swift test coverage failed"}'
    ;;
  bash|shell)
    # Shell projects — no standard coverage tool; report test pass/fail only
    TEST_SCRIPT=$(echo "$STACK" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commands',{}).get('test',''))" 2>/dev/null || echo "")
    if [ -n "$TEST_SCRIPT" ]; then
      if bash -c "$TEST_SCRIPT" > /dev/null 2>&1; then
        echo '{"pct":null,"language":"shell","note":"Shell project — no line coverage tool. Tests pass.","test_pass":true}'
      else
        echo '{"pct":null,"language":"shell","note":"Shell project — no line coverage tool. Tests FAIL.","test_pass":false}'
      fi
    else
      echo '{"pct":null,"language":"shell","note":"Shell project — no line coverage tool, no test command detected."}'
    fi
    ;;
  *)
    echo "{\"error\":\"unknown test runner: $TEST_RUNNER\",\"language\":\"$LANG\"}"
    ;;
esac
