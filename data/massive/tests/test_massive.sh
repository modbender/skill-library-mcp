#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="${ROOT_DIR}/scripts/massive"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

FAKE_BIN="${TMP_DIR}/bin"
mkdir -p "${FAKE_BIN}"

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  [[ "$haystack" == *"$needle"* ]] || fail "expected output to contain: $needle"
}

assert_not_contains() {
  local haystack="$1"
  local needle="$2"
  [[ "$haystack" != *"$needle"* ]] || fail "did not expect output to contain: $needle"
}

write_fake_curl() {
  cat >"${FAKE_BIN}/curl" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

headers=""
body=""
write_out=""
url=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dump-header)
      headers="$2"
      shift 2
      ;;
    --output)
      body="$2"
      shift 2
      ;;
    --write-out)
      write_out="$2"
      shift 2
      ;;
    --header)
      printf '%s\n' "$2" >>"${FAKE_CURL_CAPTURE}"
      shift 2
      ;;
    --silent|--show-error|--location|--user-agent|--connect-timeout|--max-time)
      shift
      [[ $# -gt 0 && "$1" != --* ]] && shift || true
      ;;
    https://*)
      url="$1"
      shift
      ;;
    *)
      shift
      ;;
  esac
done

printf '%s\n' "$url" >"${FAKE_CURL_URL}"
printf 'x-request-id: req_test\n' >"${headers}"
printf '%s' "${FAKE_CURL_BODY}" >"${body}"
printf '%s' "${FAKE_CURL_STATUS}"
EOF
  chmod +x "${FAKE_BIN}/curl"
}

export PATH="${FAKE_BIN}:$PATH"
export FAKE_CURL_CAPTURE="${TMP_DIR}/headers.txt"
export FAKE_CURL_URL="${TMP_DIR}/url.txt"
export FAKE_CURL_STATUS=""
export FAKE_CURL_BODY=""
write_fake_curl

test_health_with_env_secret() {
  local output
  output="$(
    MASSIVE_API_KEY="topsecret" \
    "${CLI}" health
  )"
  assert_contains "$output" '"ok":true'
  assert_contains "$output" '"auth":"configured"'
}

test_secret_ref_env() {
  local output
  output="$(
    OPENCLAW_MASSIVE_API_KEY="secret-from-ref" \
    MASSIVE_API_KEY_REF='{"source":"env","name":"OPENCLAW_MASSIVE_API_KEY"}' \
    "${CLI}" health
  )"
  assert_contains "$output" '"ok":true'
}

test_get_builds_query_and_redacts_logs() {
  local output stderr stdout_file
  stdout_file="${TMP_DIR}/stdout.json"
  export FAKE_CURL_STATUS="200"
  export FAKE_CURL_BODY='{"results":[{"ticker":"AAPL"}],"next_url":"https://api.massive.com/v3/reference/tickers?cursor=abc"}'
  stderr="$(
    MASSIVE_API_KEY="supersecret" \
    "${CLI}" --verbose get /v3/reference/tickers --query ticker=AAPL \
      >"${stdout_file}" 2>&1
  )"
  output="$(cat "${stdout_file}")"
  assert_contains "$output" '"ticker": "AAPL"'
  assert_contains "$(cat "${FAKE_CURL_URL}")" 'ticker=AAPL'
  assert_not_contains "$stderr" 'supersecret'
}

test_next_reads_next_url_from_stdin() {
  local output
  export FAKE_CURL_STATUS="200"
  export FAKE_CURL_BODY='{"results":[{"ticker":"MSFT"}]}'
  output="$(
    printf '%s' '{"next_url":"https://api.massive.com/v3/reference/tickers?cursor=abc"}' | \
      MASSIVE_API_KEY="topsecret" "${CLI}" next
  )"
  assert_contains "$output" '"ticker": "MSFT"'
  assert_contains "$(cat "${FAKE_CURL_URL}")" 'cursor=abc'
}

test_dry_run_never_prints_secret() {
  local output
  output="$(
    MASSIVE_API_KEY="topsecret" \
    "${CLI}" --dry-run get /v3/reference/tickers/AAPL
  )"
  assert_contains "$output" '"auth":"configured"'
  assert_not_contains "$output" 'topsecret'
}

test_rejects_absolute_url_outside_default_origin() {
  local stderr
  set +e
  stderr="$(
    MASSIVE_API_KEY="topsecret" \
    "${CLI}" get "https://example.com/v3/reference/tickers/AAPL" 2>&1
  )"
  local status=$?
  set -e
  [[ "$status" -ne 0 ]] || fail "expected command to fail for non-Massive origin"
  assert_contains "$stderr" 'absolute URL origin must match MASSIVE_BASE_URL'
}

test_allows_absolute_url_when_base_url_is_overridden() {
  local output
  export FAKE_CURL_STATUS="200"
  export FAKE_CURL_BODY='{"results":[{"ticker":"AAPL"}]}'
  output="$(
    MASSIVE_API_KEY="topsecret" \
    MASSIVE_BASE_URL="https://sandbox.massive.test" \
    "${CLI}" get "https://sandbox.massive.test/v3/reference/tickers/AAPL"
  )"
  assert_contains "$output" '"ticker": "AAPL"'
  assert_contains "$(cat "${FAKE_CURL_URL}")" 'https://sandbox.massive.test/v3/reference/tickers/AAPL'
}

test_health_with_env_secret
test_secret_ref_env
test_get_builds_query_and_redacts_logs
test_next_reads_next_url_from_stdin
test_dry_run_never_prints_secret
test_rejects_absolute_url_outside_default_origin
test_allows_absolute_url_when_base_url_is_overridden

printf 'ok\n'
