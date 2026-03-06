#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$ROOT_DIR/scripts/taapi-agent.sh"

pass_count=0
fail_count=0

pass() {
  echo "PASS: $1"
  pass_count=$((pass_count + 1))
}

fail() {
  echo "FAIL: $1" >&2
  fail_count=$((fail_count + 1))
}

expect_success() {
  local name="$1"
  shift
  local out
  set +e
  out="$("$@" 2>&1)"
  local rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    pass "$name"
  else
    echo "$out" >&2
    fail "$name (exit $rc)"
  fi
}

expect_fail_contains() {
  local name="$1"
  local pattern="$2"
  shift 2
  local out
  set +e
  out="$("$@" 2>&1)"
  local rc=$?
  set -e
  if [[ $rc -ne 0 && "$out" == *"$pattern"* ]]; then
    pass "$name"
  else
    echo "$out" >&2
    fail "$name (rc=$rc, expected pattern: $pattern)"
  fi
}

expect_success "help exits 0" "$CLI" --help
expect_fail_contains "unknown command fails" "unknown command" "$CLI" wat
expect_fail_contains "direct missing secret" "missing secret" "$CLI" direct --indicator rsi --exchange binance --symbol BTC/USDT --interval 1h
expect_fail_contains "direct crypto missing exchange" "--exchange is required" env TAAPI_SECRET=dummy "$CLI" direct --indicator rsi --symbol BTC/USDT --interval 1h
expect_fail_contains "bulk missing payload file" "missing --payload-file" env TAAPI_SECRET=dummy "$CLI" bulk
expect_fail_contains "bulk placeholder payload requires secret" "missing secret" "$CLI" bulk --payload-file "$ROOT_DIR/examples/bulk-single-construct.json"
expect_fail_contains "unofficial base URL requires explicit opt-in" "refusing unofficial base URL" env TAAPI_SECRET=dummy "$CLI" direct --indicator rsi --exchange binance --symbol BTC/USDT --interval 1h --base-url https://example.com
expect_fail_contains "unofficial base URL warns when opted in" "using unofficial TAAPI base URL" env TAAPI_SECRET=dummy "$CLI" direct --indicator rsi --exchange binance --symbol BTC/USDT --interval 1h --base-url https://example.com --allow-unofficial-base-url --retries 0 --timeout 1

if command -v jq >/dev/null 2>&1; then
  expect_fail_contains "multi missing symbols" "missing --symbols" env TAAPI_SECRET=dummy "$CLI" multi --intervals 1h --indicators rsi
else
  echo "SKIP: multi checks require jq"
fi

echo "----"
echo "passed: $pass_count"
echo "failed: $fail_count"

if [[ $fail_count -ne 0 ]]; then
  exit 1
fi
