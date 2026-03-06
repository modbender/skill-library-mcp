#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRECHECK="$SCRIPT_DIR/preflight.sh"

TITLE="${TITLE:-}"
BODY="${BODY:-}"
TAGS="${TAGS:-}"
PUBLISH_AT="${PUBLISH_AT:-}"
SETUP_URL="${SETUP_URL:-}"
PROOF_TOKEN="${PROOF_TOKEN:-}"
SETUP_ISSUE_URL="${SETUP_ISSUE_URL:-}"
DEVICE_FINGERPRINT="${DEVICE_FINGERPRINT:-$(hostname)-$(uname -s)-$(uname -m)}"
LOCAL_DAEMON_PORT="${LOCAL_DAEMON_PORT:-19090}"
X_LOCAL_TOKEN="${X_LOCAL_TOKEN:-${THIN_RUNNER_LOCAL_TOKEN:-}}"
OFFERING_ID="${OPENCLAW_OFFERING_ID:-naver-blog-writer}"
OFFERING_EXECUTE_URL="${OPENCLAW_OFFERING_EXECUTE_URL:-}"
OFFERING_API_KEY="${OPENCLAW_CORE_API_KEY:-}"
OFFERING_API_KEY_HEADER="${OPENCLAW_CORE_API_KEY_HEADER:-x-api-key}"
CONTROL_PLANE_URL="${CONTROL_PLANE_URL:-${ACP_RUNNER_SERVER_URL:-}}"
ADMIN_KEY_RAW="${ACP_ADMIN_API_KEY:-${ACP_CONTROL_PLANE_API_KEYS:-}}"
ADMIN_KEY="${ADMIN_KEY_RAW%%,*}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title)
      TITLE="$2"
      shift 2
      ;;
    --body)
      BODY="$2"
      shift 2
      ;;
    --tags)
      TAGS="$2"
      shift 2
      ;;
    --publish-at)
      PUBLISH_AT="$2"
      shift 2
      ;;
    --setup-url)
      SETUP_URL="$2"
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

if [[ -z "$TITLE" || -z "$BODY" ]]; then
  echo '{"error":"title and body are required"}'
  exit 1
fi

set +e
PRECHECK_OUTPUT="$(bash "$PRECHECK" \
  --setup-url "$SETUP_URL" \
  --proof-token "$PROOF_TOKEN" \
  --setup-issue-url "$SETUP_ISSUE_URL" \
  --device-fingerprint "$DEVICE_FINGERPRINT" \
  --local-daemon-port "$LOCAL_DAEMON_PORT" \
  --x-local-token "$X_LOCAL_TOKEN" 2>&1)"
PRECHECK_CODE=$?
set -e

if [[ $PRECHECK_CODE -ne 0 ]]; then
  printf '%s\n' "$PRECHECK_OUTPUT"
  exit $PRECHECK_CODE
fi

identity_tmp="$(mktemp)"
seal_tmp="$(mktemp)"
exec_tmp="$(mktemp)"
trap 'rm -f "$identity_tmp" "$seal_tmp" "$exec_tmp"' EXIT

identity_code="$({
  curl -sS -o "$identity_tmp" -w '%{http_code}' \
    -H "x-local-token: ${X_LOCAL_TOKEN}" \
    "http://127.0.0.1:${LOCAL_DAEMON_PORT}/v1/local/identity"
} || true)"

if [[ "$identity_code" != "200" ]]; then
  cat "$identity_tmp"
  exit 1
fi

seal_payload="$(node - "$TITLE" "$BODY" "$TAGS" "$PUBLISH_AT" <<'NODE'
const title = process.argv[2] || '';
const body = process.argv[3] || '';
const tagsRaw = process.argv[4] || '';
const publishAt = process.argv[5] || '';
const tags = tagsRaw
  .split(',')
  .map((v) => v.trim())
  .filter((v) => v.length > 0);
const payload = {
  title,
  body_markdown: body,
  tags,
  publish_at: publishAt || null,
};
process.stdout.write(JSON.stringify(payload));
NODE
)"

seal_code="$({
  curl -sS -o "$seal_tmp" -w '%{http_code}' \
    -X POST \
    -H 'content-type: application/json' \
    -H "x-local-token: ${X_LOCAL_TOKEN}" \
    -d "$seal_payload" \
    "http://127.0.0.1:${LOCAL_DAEMON_PORT}/v1/local/seal-job"
} || true)"

if [[ "$seal_code" != "200" ]]; then
  cat "$seal_tmp"
  exit 1
fi

requirement_payload="$(node - "$(cat "$identity_tmp")" "$(cat "$seal_tmp")" <<'NODE'
const identity = JSON.parse(process.argv[2]);
const sealed = JSON.parse(process.argv[3]);
const req = {
  runner_attestation: identity.runner_attestation,
  sealed_payload: sealed.sealed_payload,
  payload_digest: sealed.payload_digest,
  idempotency_key: sealed.idempotency_key,
};
process.stdout.write(JSON.stringify(req));
NODE
)"

if [[ -n "$OFFERING_EXECUTE_URL" ]]; then
  execute_body="$(node - "$OFFERING_ID" "$requirement_payload" <<'NODE'
const offeringId = process.argv[2];
const requirements = JSON.parse(process.argv[3]);
process.stdout.write(JSON.stringify({
  offering_id: offeringId,
  requirements,
}));
NODE
)"

  if [[ -n "$OFFERING_API_KEY" ]]; then
    execute_code="$({
      curl -sS -o "$exec_tmp" -w '%{http_code}' \
        -X POST \
        -H 'content-type: application/json' \
        -H "${OFFERING_API_KEY_HEADER}: ${OFFERING_API_KEY}" \
        -d "$execute_body" \
        "$OFFERING_EXECUTE_URL"
    } || true)"
  else
    execute_code="$({
      curl -sS -o "$exec_tmp" -w '%{http_code}' \
        -X POST \
        -H 'content-type: application/json' \
        -d "$execute_body" \
        "$OFFERING_EXECUTE_URL"
    } || true)"
  fi

  if [[ "$execute_code" =~ ^2 ]]; then
    cat "$exec_tmp"
    exit 0
  fi

  cat "$exec_tmp"
  exit 1
fi

if [[ -z "$CONTROL_PLANE_URL" || -z "$ADMIN_KEY" ]]; then
  echo '{"error":"OPENCLAW_OFFERING_EXECUTE_URL not set and direct dispatch creds missing"}'
  exit 1
fi

dispatch_code="$({
  curl -sS -o "$exec_tmp" -w '%{http_code}' \
    -X POST \
    -H 'content-type: application/json' \
    -H "x-api-key: ${ADMIN_KEY}" \
    -d "$requirement_payload" \
    "${CONTROL_PLANE_URL%/}/v2/jobs/dispatch-and-wait"
} || true)"

if [[ "$dispatch_code" =~ ^2 ]]; then
  cat "$exec_tmp"
  exit 0
fi

cat "$exec_tmp"
exit 1
