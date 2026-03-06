---
name: Naver Blog Writer Skill
description: 이 스킬은 ACP/OpenClaw 환경에서 네이버 블로그 발행을 자동화합니다.
---

# Naver Blog Writer Skill

이 스킬은 ACP/OpenClaw 환경에서 네이버 블로그 발행을 자동화합니다.

## Important

- ClawHub 배포본에는 보통 `SKILL.md`만 포함됩니다.
- 따라서 `tools/preflight`, `tools/publish` 같은 로컬 파일 경로를 전제로 실행하지 마세요.
- 항상 아래 **Inline Runner** 절차를 사용하세요.

## Billing Prerequisites

- 이 스킬은 ACP 유료 오퍼링(`naver-blog-writer`)입니다.
- 결제/사용 승인 후에만 온보딩 증빙이 생성됩니다.
- 온보딩 증빙(둘 중 하나 필요):
  - `SETUP_URL`
  - `PROOF_TOKEN + SETUP_ISSUE_URL`
- 결제 컨텍스트가 없으면 다음 형식으로 실패를 반환하세요:

```json
{
  "error": "RUNNER_NOT_READY",
  "setup_url": null,
  "next_action": "PURCHASE_AND_GET_SETUP_CREDENTIALS",
  "hint": "Purchase/authorize this ACP offering first, then provide SETUP_URL or PROOF_TOKEN + SETUP_ISSUE_URL.",
  "missing": ["ACP_PAYMENT_CONTEXT", "SETUP_URL_OR_PROOF_TOKEN_AND_SETUP_ISSUE_URL"]
}
```

## Runtime Config

- `OPENCLAW_OFFERING_ID` (default: `naver-blog-writer`)
- `X_LOCAL_TOKEN` (optional; 없으면 `~/.config/naver-thin-runner/config.json`에서 자동 로드)
- `LOCAL_DAEMON_PORT` (default: `19090`)
- `DEVICE_FINGERPRINT` (default: `hostname-platform-arch`)
- `OPENCLAW_OFFERING_EXECUTE_URL` (+ optional `OPENCLAW_CORE_API_KEY`)
- fallback: `CONTROL_PLANE_URL` + `ACP_ADMIN_API_KEY`

## Inline Runner (Always Use This)

아래 스크립트를 실행해 게시하세요.  
입력: `TITLE`, `BODY`, optional `TAGS` (comma separated).

```bash
bash -s -- --title "제목" --body "본문" --tags "tag1,tag2" <<'BASH'
set -euo pipefail

TITLE=''
BODY=''
TAGS=''
while [[ $# -gt 0 ]]; do
  case "$1" in
    --title) TITLE="$2"; shift 2 ;;
    --body) BODY="$2"; shift 2 ;;
    --tags) TAGS="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$TITLE" || -z "$BODY" ]]; then
  echo '{"error":"INVALID_INPUT","next_action":"PROVIDE_TITLE_AND_BODY","hint":"title and body are required"}'
  exit 1
fi

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

json_error() {
  local code="$1"; local action="$2"; local hint="$3"; local setup="${4:-}"
  node - "$code" "$action" "$hint" "$setup" <<'NODE'
const code = process.argv[2];
const action = process.argv[3];
const hint = process.argv[4];
const setup = process.argv[5] || '';
console.log(JSON.stringify({
  error: code,
  setup_url: setup || null,
  next_action: action,
  hint,
}, null, 2));
NODE
}

read_local_token() {
  node - <<'NODE'
const fs = require('node:fs');
const p = `${process.env.HOME}/.config/naver-thin-runner/config.json`;
try {
  const j = JSON.parse(fs.readFileSync(p, 'utf8'));
  process.stdout.write(typeof j.localToken === 'string' ? j.localToken.trim() : '');
} catch {
  process.stdout.write('');
}
NODE
}

runner_cmd() {
  if npx @y80163442/naver-thin-runner --help >/dev/null 2>&1; then
    npx @y80163442/naver-thin-runner "$@"
  else
    echo '{"error":"RUNNER_CLI_NOT_FOUND","next_action":"INSTALL_THIN_RUNNER","hint":"Install @y80163442/naver-thin-runner first"}'
    exit 1
  fi
}

issue_setup_url() {
  if [[ -n "$SETUP_URL" ]]; then
    printf '%s' "$SETUP_URL"; return 0
  fi
  if [[ -z "$PROOF_TOKEN" || -z "$SETUP_ISSUE_URL" ]]; then
    printf ''; return 0
  fi
  local payload
  payload="$(node - "$PROOF_TOKEN" "$DEVICE_FINGERPRINT" <<'NODE'
const proof = process.argv[2];
const fp = process.argv[3];
process.stdout.write(JSON.stringify({ proof_token: proof, device_fingerprint: fp }));
NODE
)"
  curl -sS -X POST -H 'content-type: application/json' -d "$payload" "$SETUP_ISSUE_URL" \
    | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const j=JSON.parse(d);process.stdout.write(j.setup_url||'')}catch{process.stdout.write('')}});"
}

if [[ -z "$X_LOCAL_TOKEN" ]]; then
  X_LOCAL_TOKEN="$(read_local_token)"
fi

identity_tmp="$(mktemp)"
seal_tmp="$(mktemp)"
exec_tmp="$(mktemp)"
trap 'rm -f "$identity_tmp" "$seal_tmp" "$exec_tmp"' EXIT

call_identity() {
  curl -sS --max-time 5 -o "$identity_tmp" -w '%{http_code}' \
    -H "x-local-token: ${X_LOCAL_TOKEN}" \
    "http://127.0.0.1:${LOCAL_DAEMON_PORT}/v1/local/identity" || true
}

http_code="$(call_identity)"
if [[ "$http_code" != "200" ]]; then
  # try daemon boot once
  runner_cmd daemon start --port "$LOCAL_DAEMON_PORT" >/tmp/naver-thin-runner-daemon.log 2>&1 &
  sleep 2
  http_code="$(call_identity)"
fi

if [[ "$http_code" != "200" ]]; then
  setup_url="$(issue_setup_url)"
  if [[ -z "$setup_url" && ( -z "$PROOF_TOKEN" || -z "$SETUP_ISSUE_URL" ) ]]; then
    json_error \
      "RUNNER_NOT_READY" \
      "PURCHASE_AND_GET_SETUP_CREDENTIALS" \
      "Purchase/authorize ACP offering and provide SETUP_URL or PROOF_TOKEN + SETUP_ISSUE_URL." \
      ""
    exit 2
  fi

  if [[ -n "$setup_url" ]]; then
    runner_cmd setup --setup-url "$setup_url" --auto-service both
  else
    runner_cmd setup --proof-token "$PROOF_TOKEN" --setup-issue-url "$SETUP_ISSUE_URL" --device-fingerprint "$DEVICE_FINGERPRINT" --auto-service both
  fi

  # first-time login (human action in browser)
  runner_cmd login
  X_LOCAL_TOKEN="$(read_local_token)"
  runner_cmd daemon start --port "$LOCAL_DAEMON_PORT" >/tmp/naver-thin-runner-daemon.log 2>&1 &
  sleep 2
  http_code="$(call_identity)"
fi

if [[ "$http_code" != "200" ]]; then
  json_error "RUNNER_NOT_READY" "CHECK_LOCAL_DAEMON" "Local daemon identity failed after setup/login retry." ""
  exit 2
fi

seal_payload="$(node - "$TITLE" "$BODY" "$TAGS" <<'NODE'
const title = process.argv[2] || '';
const body = process.argv[3] || '';
const tags = (process.argv[4] || '').split(',').map(v => v.trim()).filter(Boolean);
process.stdout.write(JSON.stringify({ title, body_markdown: body, tags, publish_at: null }));
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
  cat "$seal_tmp"; exit 1
fi

requirement_payload="$(node - "$(cat "$identity_tmp")" "$(cat "$seal_tmp")" <<'NODE'
const identity = JSON.parse(process.argv[2]);
const sealed = JSON.parse(process.argv[3]);
process.stdout.write(JSON.stringify({
  runner_attestation: identity.runner_attestation,
  sealed_payload: sealed.sealed_payload,
  payload_digest: sealed.payload_digest,
  idempotency_key: sealed.idempotency_key,
}));
NODE
)"

if [[ -n "$OFFERING_EXECUTE_URL" ]]; then
  execute_body="$(node - "$OFFERING_ID" "$requirement_payload" <<'NODE'
const offeringId = process.argv[2];
const requirements = JSON.parse(process.argv[3]);
process.stdout.write(JSON.stringify({ offering_id: offeringId, requirements }));
NODE
)"
  if [[ -n "$OFFERING_API_KEY" ]]; then
    curl -sS -X POST -H 'content-type: application/json' -H "${OFFERING_API_KEY_HEADER}: ${OFFERING_API_KEY}" -d "$execute_body" "$OFFERING_EXECUTE_URL"
  else
    curl -sS -X POST -H 'content-type: application/json' -d "$execute_body" "$OFFERING_EXECUTE_URL"
  fi
  exit 0
fi

if [[ -z "$CONTROL_PLANE_URL" || -z "$ADMIN_KEY" ]]; then
  json_error "EXECUTE_ENDPOINT_NOT_CONFIGURED" "CONFIGURE_EXECUTE_ENDPOINT" "Set OPENCLAW_OFFERING_EXECUTE_URL or CONTROL_PLANE_URL + ACP_ADMIN_API_KEY." ""
  exit 1
fi

curl -sS -X POST \
  -H 'content-type: application/json' \
  -H "x-api-key: ${ADMIN_KEY}" \
  -d "$requirement_payload" \
  "${CONTROL_PLANE_URL%/}/v2/jobs/dispatch-and-wait"
BASH
```

## Agent Behavior Rules

- `RUNNER_NOT_READY`면 위 Inline Runner를 통해 auto-setup/login을 먼저 시도하세요.
- 자동 복구 후에도 실패하면 원문 JSON(`error`, `next_action`, `hint`)을 사용자에게 그대로 전달하세요.
- 사람 개입이 필요한 단계는 기본적으로 네이버 로그인 1회뿐입니다.
