#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI="${SCRIPT_DIR}/eodhd"
TESTS_RUN=0

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

assert_eq() {
  local expected="$1"
  local actual="$2"
  local label="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "${expected}" != "${actual}" ]]; then
    fail "${label}: expected '${expected}' got '${actual}'"
  fi
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "${haystack}" != *"${needle}"* ]]; then
    fail "${label}: missing '${needle}'"
  fi
}

assert_not_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "${haystack}" == *"${needle}"* ]]; then
    fail "${label}: found forbidden '${needle}'"
  fi
}

run_capture() {
  local stdout_file stderr_file status
  stdout_file="$(mktemp)"
  stderr_file="$(mktemp)"

  set +o errexit
  "$@" >"${stdout_file}" 2>"${stderr_file}"
  status=$?
  set -o errexit

  printf '%s\n' "${status}"
  printf '%s\n' "${stdout_file}"
  printf '%s\n' "${stderr_file}"
}

cleanup_capture() {
  rm -f "$1" "$2"
}

main() {
  mapfile -t result < <(run_capture "${CLI}" --help)
  assert_eq "0" "${result[0]}" "help exits zero"
  assert_contains "$(cat "${result[1]}")" "services" "help lists discovery"
  assert_contains "$(cat "${result[1]}")" "live-v2" "help lists expanded command set"
  cleanup_capture "${result[1]}" "${result[2]}"

  mapfile -t result < <(run_capture "${CLI}")
  assert_eq "2" "${result[0]}" "no args exits usage"
  cleanup_capture "${result[1]}" "${result[2]}"

  mapfile -t result < <(run_capture "${CLI}" services)
  assert_eq "0" "${result[0]}" "services exits zero"
  assert_contains "$(cat "${result[1]}")" "\"service\":\"macro-indicator\"" "services includes macro-indicator"
  assert_contains "$(cat "${result[1]}")" "\"service\":\"insider-transactions\"" "services includes insider-transactions"
  cleanup_capture "${result[1]}" "${result[2]}"

  mapfile -t result < <(run_capture "${CLI}" docs calendar)
  assert_eq "0" "${result[0]}" "docs exits zero"
  assert_contains "$(cat "${result[1]}")" "\"docs_url\":\"https://eodhd.com/financial-apis/calendar-upcoming-earnings-ipos-and-splits\"" "docs prints url"
  cleanup_capture "${result[1]}" "${result[2]}"

  mapfile -t result < <(run_capture "${CLI}" eod AAPL.US)
  assert_eq "3" "${result[0]}" "missing auth exits correctly"
  assert_contains "$(cat "${result[2]}")" "EODHD_API_KEY is required" "missing auth message"
  cleanup_capture "${result[1]}" "${result[2]}"

  mapfile -t result < <(run_capture env EODHD_API_KEY=super-secret-token "${CLI}" --dry-run eod AAPL.US --from 2024-01-01 --query filter=last_close)
  assert_eq "0" "${result[0]}" "eod dry run exits zero"
  assert_contains "$(cat "${result[1]}")" "***REDACTED***" "dry run masks token"
  assert_not_contains "$(cat "${result[1]}")" "super-secret-token" "dry run hides raw token"
  assert_contains "$(cat "${result[1]}")" "/eod/AAPL.US?" "dry run includes eod path"
  cleanup_capture "${result[1]}" "${result[2]}"

  mapfile -t result < <(run_capture env EODHD_API_KEY=super-secret-token "${CLI}" --dry-run search "apple inc" --query limit=5)
  assert_eq "0" "${result[0]}" "search dry run exits zero"
  assert_contains "$(cat "${result[1]}")" "q=apple%20inc" "search encodes query"
  assert_contains "$(cat "${result[1]}")" "limit=5" "search carries arbitrary query"
  cleanup_capture "${result[1]}" "${result[2]}"

  mapfile -t result < <(run_capture env EODHD_API_KEY=super-secret-token "${CLI}" --dry-run live-v2 AAPL.US --interval 5m)
  assert_eq "0" "${result[0]}" "live-v2 dry run exits zero"
  assert_contains "$(cat "${result[1]}")" "/live/AAPL.US?" "live-v2 path"
  assert_contains "$(cat "${result[1]}")" "interval=5m" "live-v2 interval"
  cleanup_capture "${result[1]}" "${result[2]}"

  mapfile -t result < <(run_capture env EODHD_API_KEY=super-secret-token "${CLI}" --dry-run calendar earnings --from 2025-01-01 --to 2025-01-31)
  assert_eq "0" "${result[0]}" "calendar dry run exits zero"
  assert_contains "$(cat "${result[1]}")" "/calendar?" "calendar path"
  assert_contains "$(cat "${result[1]}")" "type=earnings" "calendar type"
  cleanup_capture "${result[1]}" "${result[2]}"

  mapfile -t result < <(run_capture env EODHD_API_KEY=super-secret-token "${CLI}" --dry-run macro-indicator USA --query indicator=gdp_current_usd)
  assert_eq "0" "${result[0]}" "macro indicator dry run exits zero"
  assert_contains "$(cat "${result[1]}")" "/macro-indicator/USA?" "macro path"
  assert_contains "$(cat "${result[1]}")" "indicator=gdp_current_usd" "macro query"
  cleanup_capture "${result[1]}" "${result[2]}"

  mapfile -t result < <(run_capture env EODHD_API_KEY=super-secret-token "${CLI}" --dry-run exchange-symbols US --query delisted=0)
  assert_eq "0" "${result[0]}" "exchange symbols dry run exits zero"
  assert_contains "$(cat "${result[1]}")" "/exchange-symbol-list/US?" "exchange symbols path"
  cleanup_capture "${result[1]}" "${result[2]}"

  printf 'PASS: %s smoke tests\n' "${TESTS_RUN}"
}

main "$@"
