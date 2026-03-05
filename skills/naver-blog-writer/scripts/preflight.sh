#!/usr/bin/env bash
set -euo pipefail

SETUP_URL="${SETUP_URL:-}"
PROOF_TOKEN="${PROOF_TOKEN:-}"
SETUP_ISSUE_URL="${SETUP_ISSUE_URL:-}"
DEVICE_FINGERPRINT="${DEVICE_FINGERPRINT:-$(hostname)-$(uname -s)-$(uname -m)}"
LOCAL_DAEMON_PORT="${LOCAL_DAEMON_PORT:-19090}"
X_LOCAL_TOKEN="${X_LOCAL_TOKEN:-${THIN_RUNNER_LOCAL_TOKEN:-}}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --setup-url)
      SETUP_URL="$2"
      shift 2
      ;;
    --proof-token)
      PROOF_TOKEN="$2"
      shift 2
      ;;
    --setup-issue-url)
      SETUP_ISSUE_URL="$2"
      shift 2
      ;;
    --device-fingerprint)
      DEVICE_FINGERPRINT="$2"
      shift 2
      ;;
    --local-daemon-port)
      LOCAL_DAEMON_PORT="$2"
      shift 2
      ;;
    --x-local-token)
      X_LOCAL_TOKEN="$2"
      shift 2
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

resolve_setup_url() {
  if [[ -n "$SETUP_URL" ]]; then
    printf '%s' "$SETUP_URL"
    return 0
  fi

  if [[ -z "$PROOF_TOKEN" || -z "$SETUP_ISSUE_URL" ]]; then
    printf ''
    return 0
  fi

  local tmp_body
  tmp_body="$(mktemp)"

  local payload
  payload="$(node - "$PROOF_TOKEN" "$DEVICE_FINGERPRINT" <<'NODE'
const proofToken = process.argv[2];
const deviceFingerprint = process.argv[3];
process.stdout.write(JSON.stringify({
  proof_token: proofToken,
  device_fingerprint: deviceFingerprint,
}));
NODE
)"

  local code
  code="$({
    curl -sS -o "$tmp_body" -w '%{http_code}' \
      -X POST \
      -H 'content-type: application/json' \
      -d "$payload" \
      "$SETUP_ISSUE_URL"
  } || true)"

  if [[ "$code" =~ ^2 ]]; then
    node - "$tmp_body" <<'NODE'
const fs = require('node:fs');
const body = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
process.stdout.write(typeof body.setup_url === 'string' ? body.setup_url : '');
NODE
    rm -f "$tmp_body"
    return 0
  fi

  rm -f "$tmp_body"
  printf ''
  return 0
}

emit_not_ready() {
  local resolved_setup_url
  resolved_setup_url="$(resolve_setup_url)"
  node - "$resolved_setup_url" <<'NODE'
const setupUrl = process.argv[2] || null;
console.log(JSON.stringify({
  error: 'RUNNER_NOT_READY',
  setup_url: setupUrl,
  next_action: 'RUN_SETUP',
}, null, 2));
NODE
}

if [[ -z "$X_LOCAL_TOKEN" ]]; then
  emit_not_ready
  exit 2
fi

tmp_body="$(mktemp)"
trap 'rm -f "$tmp_body"' EXIT

http_code="$({
  curl -sS --max-time 5 -o "$tmp_body" -w '%{http_code}' \
    -H "x-local-token: ${X_LOCAL_TOKEN}" \
    "http://127.0.0.1:${LOCAL_DAEMON_PORT}/v1/local/identity"
} || true)"

if [[ "$http_code" != "200" ]]; then
  emit_not_ready
  exit 2
fi

cat "$tmp_body"
