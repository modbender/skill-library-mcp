#!/usr/bin/env bash
# ============================================================
# interactive-approve.sh — Self-Evolving Agent v4.1 대화형 승인기
#
# 역할:
#   1. Discord/Telegram/Slack 제안 전송 시 인터랙티브 반응 지시 추가
#   2. `sea watch` 서브커맨드 구현:
#      - 30초 폴링으로 새 제안 감지
#      - macOS 데스크탑 알림 (osascript)
#      - 터미널 대화형 승인/거부
#
# 사용법 (직접 실행):
#   bash interactive-approve.sh --watch              # 30초 폴링 대기 모드
#   bash interactive-approve.sh --notify <prop_file> # 단일 제안 알림 + 승인 프롬프트
#   bash interactive-approve.sh --discord-footer     # Discord 리액션 지시 출력
#   bash interactive-approve.sh --telegram-buttons   # Telegram 인라인 버튼 지시 출력
#
# `sea watch` 통해 간접 호출됨.
#
# 환경변수:
#   SEA_WATCH_INTERVAL   폴링 간격 (초, 기본: 30)
#   SEA_NOTIFY_SOUND     알림 소리 on/off (기본: on)
#   TG_TOKEN             Telegram bot token (인터랙티브 버튼용)
#   TG_CHAT_ID           Telegram chat ID
#
# 변경 이력:
#   v4.1 (2026-02-18) — 신규 구현
# ============================================================

# SECURITY MANIFEST:
# Environment variables: SEA_WATCH_INTERVAL, SEA_NOTIFY_SOUND, TG_TOKEN, TG_CHAT_ID
# External endpoints: api.telegram.org (버튼 전송 시에만)
# Local files read: data/proposals/*.json
# Local files written: /tmp/sea-v4/watch-state.json

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SEA_BIN="${SKILL_DIR}/bin/sea"
PROPOSALS_DIR="${SKILL_DIR}/data/proposals"
TMP_DIR="${SEA_TMP_DIR:-/tmp/sea-v4}"
WATCH_STATE="${TMP_DIR}/watch-state.json"
WATCH_INTERVAL="${SEA_WATCH_INTERVAL:-30}"
NOTIFY_SOUND="${SEA_NOTIFY_SOUND:-on}"

# ── 색상 ──────────────────────────────────────────────────
R=$'\033[0;31m'; G=$'\033[0;32m'; Y=$'\033[1;33m'
C=$'\033[0;36m'; B=$'\033[1m';    N=$'\033[0m'

die()  { echo -e "${R}[interactive-approve] Error: $*${N}" >&2; exit 1; }
info() { echo -e "${C}[interactive-approve] $*${N}" >&2; }
ok()   { echo -e "${G}[interactive-approve] $*${N}" >&2; }
warn() { echo -e "${Y}[interactive-approve] $*${N}" >&2; }

mkdir -p "$TMP_DIR" 2>/dev/null || true

# ── Python 존재 확인 ──────────────────────────────────────
HAS_PY=false
command -v python3 &>/dev/null && HAS_PY=true || true

# ── macOS 데스크탑 알림 ───────────────────────────────────
notify_desktop() {
  local title="$1" body="$2"
  if command -v osascript &>/dev/null; then
    local sound_cmd=""
    [ "$NOTIFY_SOUND" = "on" ] && sound_cmd='sound name "Glass"' || true
    osascript -e "display notification \"${body//\"/\\\"}\" with title \"${title//\"/\\\"}\" ${sound_cmd}" \
      2>/dev/null || true
  fi
}

# ── 제안 파일 목록 (pending만) ────────────────────────────
get_pending_proposals() {
  local result=()
  for f in "$PROPOSALS_DIR"/*.json; do
    [ -f "$f" ] || continue
    local status
    if $HAS_PY; then
      status=$(python3 -c "import json; print(json.load(open('$f')).get('status','pending'))" 2>/dev/null || echo "pending")
    else
      status=$(grep -o '"status": *"[^"]*"' "$f" 2>/dev/null | head -1 | grep -o '"[^"]*"$' | tr -d '"' || echo "pending")
    fi
    [ "$status" = "pending" ] && result+=("$f") || true
  done
  printf '%s\n' "${result[@]:-}"
}

# ── 제안 필드 추출 ────────────────────────────────────────
pfield() {
  local file="$1" key="$2"
  $HAS_PY && python3 -c "import json; d=json.load(open('$1')); print(d.get('$2',''))" 2>/dev/null || echo ""
}

# ── watch-state: 이미 알림 보낸 제안 추적 ────────────────
is_notified() {
  local pid="$1"
  [ -f "$WATCH_STATE" ] || return 1
  grep -q "\"${pid}\"" "$WATCH_STATE" 2>/dev/null
}

mark_notified() {
  local pid="$1" now
  now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  if [ ! -f "$WATCH_STATE" ]; then
    echo "{\"notified\":[\"${pid}\"],\"last_check\":\"${now}\"}" > "$WATCH_STATE"
  elif $HAS_PY; then
    python3 - "$WATCH_STATE" "$pid" "$now" <<'PYEOF'
import json, sys
path, pid, now = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(path))
if pid not in d.get("notified", []):
    d.setdefault("notified", []).append(pid)
d["last_check"] = now
json.dump(d, open(path, 'w'))
PYEOF
  else
    # シンプルなフォールバック: ファイルに追記
    echo "\"${pid}\"" >> "$WATCH_STATE" 2>/dev/null || true
  fi
}

# ── 터미널 대화형 승인 ────────────────────────────────────
interactive_prompt() {
  local file="$1"
  local id title severity section before after
  id=$(pfield "$file" id)
  title=$(pfield "$file" title)
  severity=$(pfield "$file" severity)
  section=$(pfield "$file" section)
  before=$(pfield "$file" before)
  after=$(pfield "$file" after)

  echo ""
  echo -e "${B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${N}"
  echo -e "${B}🆕 새 제안 도착${N}"
  echo -e "${B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${N}"
  echo -e "  ${B}ID:${N}       ${C}${id}${N}"
  echo -e "  ${B}제목:${N}     ${title}"
  echo -e "  ${B}심각도:${N}   ${Y}${severity}${N}"
  echo -e "  ${B}섹션:${N}     ${section}"
  echo ""

  if [ -n "$before" ] || [ -n "$after" ]; then
    echo -e "${B}--- Before ---${N}"
    echo "$before" | head -15
    echo -e "\n${B}+++ After  ---${N}"
    echo "$after" | head -15
    echo ""
  fi

  echo -e "${B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${N}"
  echo -e "  ${G}[a]${N} 승인 (approve)   ${R}[r]${N} 거부 (reject)   ${C}[s]${N} 건너뜀 (skip)"
  echo -e "${B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${N}"
  printf "선택 [a/r/s]: "
  read -r choice </dev/tty 2>/dev/null || { warn "TTY 없음 — 건너뜀"; return 0; }

  case "${choice,,}" in
    a|approve|y|yes)
      info "승인: $id"
      bash "$SEA_BIN" approve "$id" 2>&1 || warn "sea approve 실패 (수동 확인 필요)"
      ok "✅ 제안 승인됨: $id"
      ;;
    r|reject|n|no)
      printf "거부 이유를 입력하세요: "
      read -r reason </dev/tty 2>/dev/null || reason="사용자 거부 (watch 모드)"
      [ -z "$reason" ] && reason="사용자 거부 (watch 모드)"
      bash "$SEA_BIN" reject "$id" "$reason" 2>&1 || warn "sea reject 실패"
      ok "❌ 제안 거부됨: $id"
      ;;
    s|skip|*)
      warn "건너뜀: $id"
      ;;
  esac
}

# ── Discord 리액션 지시 푸터 ──────────────────────────────
discord_footer() {
  # synthesize-proposal.sh 출력 끝에 추가할 Discord 리액션 지시
  cat <<'FOOTER'

---

## 💬 승인 방법

> Discord 리액션으로 즉시 응답하세요:
>
> ✅ **리액션** → 이 제안 **승인** (자동으로 `sea approve` 실행)
> ❌ **리액션** → 이 제안 **거부**
> 🔍 **리액션** → diff 전체 보기 (스레드로 확장)
>
> 또는 터미널에서: `sea watch` (대화형 승인)

FOOTER
}

# ── Telegram 인라인 버튼 페이로드 생성 ───────────────────
# proposal ID를 callback_data에 포함하는 Telegram 인라인 키보드
telegram_inline_buttons() {
  local prop_id="${1:-unknown}"
  local short_id="${prop_id:0:20}"  # Telegram callback_data 64바이트 제한

  python3 - "$prop_id" "$short_id" <<'PYEOF' 2>/dev/null || echo "{}"
import json, sys
prop_id, short_id = sys.argv[1], sys.argv[2]
keyboard = {
    "inline_keyboard": [
        [
            {"text": "✅ 승인",   "callback_data": f"sea_approve:{short_id}"},
            {"text": "❌ 거부",   "callback_data": f"sea_reject:{short_id}"},
            {"text": "🔍 diff",   "callback_data": f"sea_diff:{short_id}"}
        ]
    ]
}
print(json.dumps(keyboard))
PYEOF
}

# ── Telegram 버튼 포함 전송 ───────────────────────────────
send_telegram_with_buttons() {
  local text="$1" prop_id="${2:-}"
  local tg_token="${TG_TOKEN:-${SEA_TG_BOT_TOKEN:-}}"
  local tg_chat="${TG_CHAT_ID:-${SEA_TG_CHAT_ID:-}}"

  [ -z "$tg_token" ] && { warn "TG_TOKEN 미설정 — 버튼 없이 전송됨"; return 1; }
  [ -z "$tg_chat"  ] && { warn "TG_CHAT_ID 미설정"; return 1; }

  local keyboard
  keyboard=$(telegram_inline_buttons "$prop_id")

  # Python 스크립트를 임시 파일로 작성 (heredoc-in-$() 회피)
  local _py_script; _py_script=$(mktemp /tmp/sea-tg-payload.XXXXXX.py)
  cat > "$_py_script" <<'ENDPY'
import json, re, sys
chat_id, text_raw, keyboard_json = sys.argv[1], sys.argv[2], sys.argv[3]
t = re.sub(r'^#{1,3} (.+)$', r'<b>\1</b>', text_raw, flags=re.MULTILINE)
t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
keyboard = json.loads(keyboard_json)
payload = {
    "chat_id": chat_id,
    "text": t[:4096],
    "parse_mode": "HTML",
    "reply_markup": keyboard
}
print(json.dumps(payload))
ENDPY

  local payload
  payload=$(python3 "$_py_script" "$tg_chat" "$text" "$keyboard" 2>/dev/null)
  rm -f "$_py_script"

  if [ -z "$payload" ]; then
    warn "Telegram payload 생성 실패"
    return 1
  fi

  curl -sf -X POST \
    "https://api.telegram.org/bot${tg_token}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    --max-time 15 > /dev/null 2>&1 \
    && ok "Telegram 버튼 포함 전송 완료" \
    || warn "Telegram 전송 실패"
}

# ── Telegram Callback 처리 안내 ───────────────────────────
# 실제 버튼 클릭 처리는 Telegram webhook 또는 long-polling이 필요.
# 이 스크립트는 버튼 페이로드를 생성하고, OpenClaw 크론이나
# 별도 봇 서버에서 콜백을 받아 `sea approve/reject <id>` 를 실행해야 함.
#
# 권장: OpenClaw heartbeat에서 아래 패턴으로 처리
#   sea approve prop-YYYYMMDD-NNN   # callback_data "sea_approve:prop-YYYYMMDD-NNN"
#   sea reject  prop-YYYYMMDD-NNN "이유"

# ══════════════════════════════════════════════════════════
# sea watch 메인 루프
# ══════════════════════════════════════════════════════════
cmd_watch() {
  echo -e "${B}👁  sea watch 시작${N} — ${WATCH_INTERVAL}초마다 새 제안 확인"
  echo -e "    종료: Ctrl+C"
  echo ""

  # 시작 시 이미 있는 pending 제안 처리
  local initial_shown=false
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    local pid
    pid=$(pfield "$f" id)
    if ! is_notified "$pid" 2>/dev/null; then
      if [ "$initial_shown" = false ]; then
        echo -e "${Y}📋 기존 미처리 제안 발견:${N}"
        initial_shown=true
      fi
      local title
      title=$(pfield "$f" title)
      echo -e "  ${C}${pid}${N}: ${title}"
      notify_desktop "🧠 Self-Evolving Agent" "미처리 제안: ${title}"
      interactive_prompt "$f"
      mark_notified "$pid"
    fi
  done < <(get_pending_proposals)

  [ "$initial_shown" = false ] && echo -e "${G}✅ 현재 미처리 제안 없음${N}" || true
  echo ""
  echo -e "${C}⏱  대기 중... (${WATCH_INTERVAL}초 폴링)${N}"

  # 폴링 루프
  while true; do
    sleep "$WATCH_INTERVAL" 2>/dev/null || break

    local found_new=false
    while IFS= read -r f; do
      [ -z "$f" ] && continue
      local pid
      pid=$(pfield "$f" id)
      if ! is_notified "$pid" 2>/dev/null; then
        found_new=true
        local title sev
        title=$(pfield "$f" title)
        sev=$(pfield "$f" severity)

        echo ""
        ok "🆕 새 제안 감지: ${pid}"
        notify_desktop "🧠 새 제안 도착 (${sev})" "${title}"
        interactive_prompt "$f"
        mark_notified "$pid"
      fi
    done < <(get_pending_proposals)

    if [ "$found_new" = false ]; then
      local now
      now=$(TZ="Asia/Seoul" date "+%H:%M:%S" 2>/dev/null || date "+%H:%M:%S")
      printf "\r${C}⏱  [%s] 새 제안 없음 — %s초 후 재확인${N}   " "$now" "$WATCH_INTERVAL"
    fi
  done
}

# ── 단일 제안 알림 ────────────────────────────────────────
cmd_notify() {
  local file="${1:-}"
  [ -z "$file" ] && die "--notify <proposal_file> 필요"
  [ -f "$file" ] || die "파일 없음: $file"

  local id title sev
  id=$(pfield "$file" id)
  title=$(pfield "$file" title)
  sev=$(pfield "$file" severity)

  notify_desktop "🧠 Self-Evolving Agent [${sev}]" "${title}"
  interactive_prompt "$file"
}

# ── 메인 ─────────────────────────────────────────────────
case "${1:-}" in
  --watch)           cmd_watch ;;
  --notify)          cmd_notify "${2:-}" ;;
  --discord-footer)  discord_footer ;;
  --telegram-buttons) telegram_inline_buttons "${2:-unknown}" ;;
  --send-telegram)
    shift
    send_telegram_with_buttons "${1:-}" "${2:-}" ;;
  --help|-h)
    cat <<EOF
Usage: bash interactive-approve.sh [OPTION]

  --watch                  30초 폴링, 새 제안 대화형 승인 (sea watch)
  --notify <file>          단일 제안 파일 알림 + 승인 프롬프트
  --discord-footer         Discord 리액션 지시 푸터 출력
  --telegram-buttons <id>  Telegram 인라인 버튼 JSON 출력
  --send-telegram <text> <id>  Telegram 버튼 포함 전송
  --help                   이 도움말

환경변수:
  SEA_WATCH_INTERVAL   폴링 간격 (기본: 30초)
  SEA_NOTIFY_SOUND     알림 소리 on/off
  TG_TOKEN             Telegram bot token
  TG_CHAT_ID           Telegram chat ID
EOF
    ;;
  *)
    # 기본: watch 모드
    cmd_watch ;;
esac
