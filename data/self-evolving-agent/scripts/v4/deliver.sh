#!/usr/bin/env bash
# ============================================================
# deliver.sh — Self-Evolving Agent v4.0 멀티플랫폼 배달기
#
# 역할: 제안 마크다운을 설정된 플랫폼으로 전송.
#       Discord는 OpenClaw 네이티브 배달을 사용하므로 이 스크립트 불필요.
#       Slack / Telegram / Webhook 전용 핸들러.
#
# 사용법:
#   bash deliver.sh [proposal_file]       # 파일 지정
#   cat proposal.md | bash deliver.sh     # stdin
#   PLATFORM=slack bash deliver.sh file  # 플랫폼 강제 지정 (테스트용)
#
# 환경변수 (config.yaml에서 자동 로드, 오버라이드 가능):
#   PLATFORM      — slack | telegram | webhook
#   SLACK_URL     — Slack Incoming Webhook URL
#   TG_TOKEN      — Telegram bot token
#   TG_CHAT_ID    — Telegram chat ID
#   WEBHOOK_URL   — Generic webhook URL
#
# 배달 실패 시:
#   data/undelivered/YYYYMMDD-HHMMSS.md 에 저장 (유실 방지)
#
# 변경 이력:
#   v4.1 (2026-02-18) — 신규 구현 (멀티플랫폼 배달 지원)
# ============================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
UNDELIVERED_DIR="${SKILL_DIR}/data/undelivered"

# ── config.yaml 로딩 ──────────────────────────────────────
_CONFIG_LOADER="${SKILL_DIR}/scripts/lib/config-loader.sh"
if [[ -f "$_CONFIG_LOADER" ]]; then
  source "$_CONFIG_LOADER" 2>/dev/null || true
  sea_load_config 2>/dev/null || true
fi

# ── 설정값 (환경변수 > config.yaml > 기본값) ──────────────
PLATFORM="${PLATFORM:-${SEA_DELIVERY_PLATFORM:-discord}}"
SLACK_URL="${SLACK_URL:-${SEA_SLACK_WEBHOOK_URL:-}}"
TG_TOKEN="${TG_TOKEN:-${SEA_TG_BOT_TOKEN:-}}"
TG_CHAT_ID="${TG_CHAT_ID:-${SEA_TG_CHAT_ID:-}}"
WEBHOOK_URL="${WEBHOOK_URL:-${SEA_WEBHOOK_URL:-}}"
WEBHOOK_METHOD="${WEBHOOK_METHOD:-${SEA_WEBHOOK_METHOD:-POST}}"

# ── 제안 내용 읽기 (파일 또는 stdin) ──────────────────────
if [[ -n "${1:-}" && -f "$1" ]]; then
  PROPOSAL_TEXT="$(cat "$1")"
elif [[ ! -t 0 ]]; then
  PROPOSAL_TEXT="$(cat)"
else
  echo "[deliver] ERROR: 제안 내용 없음 (파일 경로 또는 stdin 필요)" >&2
  exit 1
fi

if [[ -z "${PROPOSAL_TEXT:-}" ]]; then
  echo "[deliver] ERROR: 제안 내용이 비어 있음" >&2
  exit 1
fi

# ── 실패 시 저장 함수 ──────────────────────────────────────
save_undelivered() {
  local _reason="$1"
  mkdir -p "$UNDELIVERED_DIR" 2>/dev/null || true
  local _fname="${UNDELIVERED_DIR}/$(date +%Y%m%d-%H%M%S)-${PLATFORM}.md"
  printf '%s\n\n---\n_Undelivered reason: %s_\n' "$PROPOSAL_TEXT" "$_reason" > "$_fname" 2>/dev/null || true
  echo "[deliver] 미전송 저장: ${_fname}" >&2
}

# ── Slack 핸들러 ───────────────────────────────────────────
# markdown → mrkdwn: 헤더(##) → *bold*, 코드블록 그대로 유지
deliver_slack() {
  [[ -z "$SLACK_URL" ]] && { echo "[deliver] ERROR: slack.webhook_url 미설정" >&2; return 1; }

  # 마크다운을 Slack mrkdwn으로 단순 변환
  local _mrkdwn
  _mrkdwn="$(echo "$PROPOSAL_TEXT" \
    | sed 's/^### \(.*\)$/*\1*/g' \
    | sed 's/^## \(.*\)$/*\1*/g' \
    | sed 's/^# \(.*\)$/*\1*/g' \
    | sed 's/\*\*\(.*\)\*\*/*\1*/g')"

  local _payload
  _payload="$(python3 -c "
import json, sys
text = sys.argv[1]
print(json.dumps({'text': text, 'mrkdwn': True}))
" "$_mrkdwn" 2>/dev/null)" || _payload="{\"text\": \"SEA v4.0 제안 (직렬화 실패)\"}"

  curl -sf -X POST \
    -H "Content-Type: application/json" \
    -d "$_payload" \
    "$SLACK_URL" \
    --max-time 15 \
    > /dev/null 2>&1
}

# ── Telegram 핸들러 ────────────────────────────────────────
# markdown → HTML: **bold** → <b>bold</b>, `code` → <code>code</code>
deliver_telegram() {
  [[ -z "$TG_TOKEN" ]]   && { echo "[deliver] ERROR: telegram.bot_token 미설정" >&2; return 1; }
  [[ -z "$TG_CHAT_ID" ]] && { echo "[deliver] ERROR: telegram.chat_id 미설정" >&2; return 1; }

  # Python으로 마크다운→HTML 변환 + JSON 직렬화 (한 번에)
  local _payload
  _payload="$(python3 -c "
import json, re, sys
t = sys.argv[1]
t = re.sub(r'^#{1,3} (.+)$', r'<b>\1</b>', t, flags=re.MULTILINE)
t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
t = re.sub(r'\x60([^\x60]+)\x60', r'<code>\1</code>', t)
print(json.dumps({'chat_id': sys.argv[2], 'text': t, 'parse_mode': 'HTML'}))
" "$PROPOSAL_TEXT" "$TG_CHAT_ID" 2>/dev/null)" || {
    echo "[deliver] ERROR: Telegram payload 직렬화 실패" >&2; return 1
  }

  curl -sf -X POST \
    "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "$_payload" --max-time 15 > /dev/null 2>&1
}

# ── Generic Webhook 핸들러 ─────────────────────────────────
deliver_webhook() {
  [[ -z "$WEBHOOK_URL" ]] && { echo "[deliver] ERROR: webhook.url 미설정" >&2; return 1; }

  local _payload
  _payload="$(python3 -c "
import json, sys
print(json.dumps({
    'source': 'self-evolving-agent',
    'version': '4.0',
    'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
    'proposal': sys.argv[1],
}))
" "$PROPOSAL_TEXT" 2>/dev/null)" || _payload="{\"source\":\"self-evolving-agent\",\"proposal\":\"직렬화 실패\"}"

  curl -sf -X "${WEBHOOK_METHOD}" \
    -H "Content-Type: application/json" \
    -d "$_payload" \
    "$WEBHOOK_URL" \
    --max-time 15 \
    > /dev/null 2>&1
}

# ── 플랫폼별 디스패치 ──────────────────────────────────────
echo "[deliver] 플랫폼: ${PLATFORM}" >&2

case "$PLATFORM" in
  discord)
    # Discord는 OpenClaw 네이티브 배달 사용 → 이 스크립트 불필요
    # orchestrator.sh에서 호출 안 하지만, 직접 실행 시 안내
    echo "[deliver] Discord는 OpenClaw 네이티브 배달 사용 (deliver.sh 불필요)" >&2
    exit 0
    ;;
  slack)
    deliver_slack && echo "[deliver] Slack 전송 성공" >&2 || {
      save_undelivered "Slack curl 실패"
      exit 1
    }
    ;;
  telegram)
    deliver_telegram && echo "[deliver] Telegram 전송 성공" >&2 || {
      save_undelivered "Telegram curl 실패"
      exit 1
    }
    ;;
  webhook)
    deliver_webhook && echo "[deliver] Webhook 전송 성공" >&2 || {
      save_undelivered "Webhook curl 실패"
      exit 1
    }
    ;;
  *)
    echo "[deliver] ERROR: 알 수 없는 플랫폼: ${PLATFORM}" >&2
    save_undelivered "알 수 없는 플랫폼: ${PLATFORM}"
    exit 1
    ;;
esac

exit 0
