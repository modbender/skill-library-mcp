#!/usr/bin/env bash
# ============================================================
# setup-wizard.sh — Self-Evolving Agent 초기 설정 마법사 v1.0
#
# 역할: 최초 설치 시 대화형으로 config.yaml을 생성하고 크론을 등록.
#
# 사용법:
#   bash setup-wizard.sh                              # 대화형 모드
#   bash setup-wizard.sh --channel 123 --platform discord --lang auto  # 비대화형
#
# 옵션 (비대화형):
#   --workspace DIR   OpenClaw 워크스페이스 경로 (기본: ~/openclaw)
#   --platform PLAT   플랫폼: discord|slack|telegram|webhook (기본: discord)
#   --channel ID      Discord 채널 ID
#   --webhook URL     Slack Webhook URL 또는 generic webhook URL
#   --tg-token TOKEN  Telegram bot token
#   --tg-chat ID      Telegram chat_id
#   --days N          분석 기간 일수 (기본: 7)
#   --max-sessions N  최대 세션 수 (기본: 30)
#   --lang LANG       주요 언어: ko|en|auto (기본: auto)
#   --schedule EXPR   크론 표현식 (기본: "0 22 * * 0")
#   --no-cron         크론 등록 생략
#   --yes             모든 확인에 자동 yes
#
# 종료 코드:
#   0 — 설정 완료
#   1 — 사용자 취소 또는 오류
# ============================================================

# SECURITY MANIFEST:
# Environment variables accessed: SEA_CONFIG, HOME
# External endpoints called: None
# Local files read:
#   ~/openclaw/skills/self-evolving-agent/config.yaml  (기존 설정 읽기)
#   ~/openclaw/skills/self-evolving-agent/scripts/lib/config-loader.sh
# Local files written:
#   ~/openclaw/skills/self-evolving-agent/config.yaml  (설정 저장)
#   ~/openclaw/skills/self-evolving-agent/config.yaml.bak.wizard  (백업)
# Network: None

# !! set -euo pipefail 미사용 — read -p 대화형 입력에 영향줄 수 있음 !!

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="${SEA_CONFIG:-$SKILL_DIR/config.yaml}"

# ── 색상/스타일 (터미널 지원 시) ────────────────────────────
if [ -t 1 ] && [ -t 2 ]; then
  BOLD='\033[1m'
  DIM='\033[2m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  RED='\033[0;31m'
  CYAN='\033[0;36m'
  RESET='\033[0m'
else
  BOLD='' DIM='' GREEN='' YELLOW='' RED='' CYAN='' RESET=''
fi

# ── 기본값 ───────────────────────────────────────────────────
OPT_WORKSPACE="$HOME/openclaw"
OPT_PLATFORM="discord"
OPT_CHANNEL=""
OPT_WEBHOOK=""
OPT_TG_TOKEN=""
OPT_TG_CHAT=""
OPT_DAYS="7"
OPT_MAX_SESSIONS="30"
OPT_LANG="auto"
OPT_SCHEDULE="0 22 * * 0"
OPT_NO_CRON=false
OPT_YES=false
INTERACTIVE=true

# ── 옵션 파싱 ───────────────────────────────────────────────
parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --workspace)   OPT_WORKSPACE="$2";    shift 2 ;;
      --platform)    OPT_PLATFORM="$2";     shift 2 ;;
      --channel)     OPT_CHANNEL="$2";      shift 2 ;;
      --webhook)     OPT_WEBHOOK="$2";      shift 2 ;;
      --tg-token)    OPT_TG_TOKEN="$2";     shift 2 ;;
      --tg-chat)     OPT_TG_CHAT="$2";      shift 2 ;;
      --days)        OPT_DAYS="$2";         shift 2 ;;
      --max-sessions) OPT_MAX_SESSIONS="$2"; shift 2 ;;
      --lang)        OPT_LANG="$2";         shift 2 ;;
      --schedule)    OPT_SCHEDULE="$2";     shift 2 ;;
      --no-cron)     OPT_NO_CRON=true;      shift ;;
      --yes|-y)      OPT_YES=true;          shift ;;
      --help|-h)
        echo "사용법: $0 [옵션]"
        echo ""
        echo "대화형 (옵션 없이):"
        echo "  bash $0"
        echo ""
        echo "비대화형:"
        echo "  bash $0 --platform discord --channel 123456789 --lang auto"
        echo "  bash $0 --platform slack --webhook https://hooks.slack.com/..."
        echo "  bash $0 --platform telegram --tg-token 123:ABC --tg-chat -100123"
        echo ""
        echo "옵션:"
        echo "  --workspace DIR   OpenClaw 워크스페이스 (기본: ~/openclaw)"
        echo "  --platform PLAT   discord|slack|telegram|webhook (기본: discord)"
        echo "  --channel ID      Discord 채널 ID"
        echo "  --webhook URL     Slack/webhook URL"
        echo "  --tg-token TOKEN  Telegram bot token"
        echo "  --tg-chat ID      Telegram chat_id"
        echo "  --days N          분석 기간 1-90 (기본: 7)"
        echo "  --max-sessions N  최대 세션 수 1-200 (기본: 30)"
        echo "  --lang LANG       ko|en|auto (기본: auto)"
        echo "  --schedule EXPR   크론 표현식 (기본: \"0 22 * * 0\")"
        echo "  --no-cron         크론 등록 생략"
        echo "  --yes             모든 확인에 자동 yes"
        exit 0
        ;;
      *)
        echo "알 수 없는 옵션: $1" >&2
        echo "도움말: $0 --help" >&2
        exit 1
        ;;
    esac
  done

  # 비대화형 모드 감지: 핵심 옵션 중 하나라도 있으면
  if [ -n "$OPT_CHANNEL" ] || [ -n "$OPT_WEBHOOK" ] || [ -n "$OPT_TG_TOKEN" ]; then
    INTERACTIVE=false
  fi
}

# ── 입력 유틸 ───────────────────────────────────────────────
prompt_input() {
  local prompt="$1"
  local default="$2"
  local varname="$3"
  local result

  if [ -n "$default" ]; then
    printf "%b%s [%s%s%s]: %b" "$CYAN" "$prompt" "$BOLD" "$default" "$RESET$CYAN" "$RESET"
  else
    printf "%b%s: %b" "$CYAN" "$prompt" "$RESET"
  fi

  read -r result
  result="${result:-$default}"
  printf -v "$varname" '%s' "$result"
}

prompt_yesno() {
  local prompt="$1"
  local default="${2:-y}"  # y 또는 n
  local result

  if [ "$OPT_YES" = "true" ]; then
    echo "$default" | tr '[:lower:]' '[:upper:]'
    return 0
  fi

  local default_upper
  default_upper="$(echo "$default" | tr '[:lower:]' '[:upper:]')"
  printf "%b%s [%s]: %b" "$CYAN" "$prompt" "$default_upper" "$RESET"
  read -r result
  result="${result:-$default}"
  echo "$result" | tr '[:upper:]' '[:lower:]' | grep -qE '^(y|yes)$'
}

# ── 검증 함수 ────────────────────────────────────────────────
validate_platform() {
  local p
  p="$(echo "$1" | tr '[:upper:]' '[:lower:]')"
  echo "$p" | grep -qE '^(discord|slack|telegram|webhook)$'
}

validate_days() {
  local d="$1"
  echo "$d" | grep -qE '^[0-9]+$' && [ "$d" -ge 1 ] && [ "$d" -le 90 ]
}

validate_max_sessions() {
  local m="$1"
  echo "$m" | grep -qE '^[0-9]+$' && [ "$m" -ge 1 ] && [ "$m" -le 200 ]
}

validate_lang() {
  local l
  l="$(echo "$1" | tr '[:upper:]' '[:lower:]')"
  echo "$l" | grep -qE '^(ko|en|auto)$'
}

validate_channel_id() {
  local c="$1"
  # Discord 채널 ID: 숫자만, 17-19자리
  echo "$c" | grep -qE '^[0-9]{17,19}$'
}

validate_discord_not_old() {
  local c="$1"
  [ "$c" != "1469905074661757049" ]
}

validate_cron_expr() {
  local expr="$1"
  # 최소 검증: 5개 필드 (공백으로 구분)
  local field_count
  field_count=$(echo "$expr" | awk '{print NF}')
  [ "$field_count" -eq 5 ]
}

# ── Step 1: 워크스페이스 ─────────────────────────────────────
step_workspace() {
  echo ""
  echo "${BOLD}1. OpenClaw 워크스페이스 경로${RESET}"

  local ws="$OPT_WORKSPACE"
  if [ "$INTERACTIVE" = "true" ]; then
    while true; do
      prompt_input "워크스페이스 경로" "$ws" ws
      ws="${ws/#\~/$HOME}"  # ~ 확장
      if [ -d "$ws" ]; then
        break
      else
        echo "   ${YELLOW}⚠️  디렉토리 없음: $ws${RESET}"
        if prompt_yesno "   계속 진행하겠습니까?" "n"; then
          break
        fi
        ws="$OPT_WORKSPACE"
      fi
    done
  else
    ws="${ws/#\~/$HOME}"
  fi

  OPT_WORKSPACE="$ws"
  echo "   ${GREEN}✓${RESET} 워크스페이스: $OPT_WORKSPACE"
}

# ── Step 2: 플랫폼 ──────────────────────────────────────────
step_platform() {
  echo ""
  echo "${BOLD}2. 결과 전송 플랫폼${RESET}"
  echo "   ${DIM}선택지: discord / slack / telegram / webhook${RESET}"

  local p="$OPT_PLATFORM"
  if [ "$INTERACTIVE" = "true" ]; then
    while true; do
      prompt_input "플랫폼" "$p" p
      p="$(echo "$p" | tr '[:upper:]' '[:lower:]')"
      if validate_platform "$p"; then
        break
      else
        echo "   ${RED}❌ 유효하지 않음. discord/slack/telegram/webhook 중 선택${RESET}"
      fi
    done
  else
    p="$(echo "$p" | tr '[:upper:]' '[:lower:]')"
    if ! validate_platform "$p"; then
      echo "${RED}❌ 유효하지 않은 플랫폼: $p${RESET}" >&2
      exit 1
    fi
  fi

  OPT_PLATFORM="$p"
  echo "   ${GREEN}✓${RESET} 플랫폼: $OPT_PLATFORM"
}

# ── Step 3: 플랫폼별 인증 정보 ──────────────────────────────
step_credentials() {
  echo ""
  echo "${BOLD}3. 인증 정보${RESET}"

  case "$OPT_PLATFORM" in
    discord)
      local ch="$OPT_CHANNEL"
      if [ "$INTERACTIVE" = "true" ]; then
        while true; do
          prompt_input "Discord 채널 ID (17-19자리 숫자)" "$ch" ch
          if ! validate_channel_id "$ch"; then
            echo "   ${YELLOW}⚠️  형식이 맞지 않습니다 (17-19자리 숫자 권장)${RESET}"
            if prompt_yesno "   그래도 계속 진행하겠습니까?" "n"; then
              break
            fi
            continue
          fi
          if ! validate_discord_not_old "$ch"; then
            echo "   ${RED}❌ 구 하드코딩 채널 ID입니다. 올바른 채널 ID를 입력하세요.${RESET}"
            echo "   ${DIM}Discord > 채널 오른쪽 클릭 > ID 복사${RESET}"
            continue
          fi
          break
        done
      else
        if [ -z "$ch" ]; then
          echo "${RED}❌ Discord 채널 ID 필요: --channel ID${RESET}" >&2
          exit 1
        fi
        if ! validate_discord_not_old "$ch"; then
          echo "${RED}❌ 구 하드코딩 채널 ID 사용 불가: $ch${RESET}" >&2
          exit 1
        fi
      fi
      OPT_CHANNEL="$ch"
      echo "   ${GREEN}✓${RESET} Discord 채널 ID: $OPT_CHANNEL"
      ;;

    slack)
      local wh="$OPT_WEBHOOK"
      if [ "$INTERACTIVE" = "true" ]; then
        echo "   ${DIM}https://api.slack.com/messaging/webhooks 에서 Webhook URL 생성${RESET}"
        while true; do
          prompt_input "Slack Webhook URL" "$wh" wh
          if echo "$wh" | grep -q "^https://hooks.slack.com/"; then
            break
          else
            echo "   ${RED}❌ https://hooks.slack.com/... 형식이어야 합니다${RESET}"
          fi
        done
      else
        if [ -z "$wh" ] || ! echo "$wh" | grep -q "^https://hooks.slack.com/"; then
          echo "${RED}❌ 유효한 Slack Webhook URL 필요: --webhook https://hooks.slack.com/...${RESET}" >&2
          exit 1
        fi
      fi
      OPT_WEBHOOK="$wh"
      echo "   ${GREEN}✓${RESET} Slack Webhook: ${wh:0:40}..."
      ;;

    telegram)
      local tg_tok="$OPT_TG_TOKEN"
      local tg_chat="$OPT_TG_CHAT"
      if [ "$INTERACTIVE" = "true" ]; then
        echo "   ${DIM}BotFather에서 발급한 토큰 (예: 123456:ABC-DEF...)${RESET}"
        while true; do
          prompt_input "Telegram Bot Token" "$tg_tok" tg_tok
          if echo "$tg_tok" | grep -qE '^[0-9]+:[A-Za-z0-9_-]+$'; then
            break
          else
            echo "   ${RED}❌ 형식: 숫자:문자열 (예: 123456:ABC-DEF...)${RESET}"
          fi
        done
        echo "   ${DIM}채널 또는 채팅방 ID (채널은 -100으로 시작)${RESET}"
        while true; do
          prompt_input "Telegram Chat ID" "$tg_chat" tg_chat
          if echo "$tg_chat" | grep -qE '^-?[0-9]+$'; then
            break
          else
            echo "   ${RED}❌ 숫자여야 합니다 (예: -1001234567890)${RESET}"
          fi
        done
      else
        if [ -z "$tg_tok" ] || [ -z "$tg_chat" ]; then
          echo "${RED}❌ Telegram bot_token + chat_id 모두 필요: --tg-token TOKEN --tg-chat ID${RESET}" >&2
          exit 1
        fi
      fi
      OPT_TG_TOKEN="$tg_tok"
      OPT_TG_CHAT="$tg_chat"
      echo "   ${GREEN}✓${RESET} Telegram bot_token: ...${tg_tok: -8}"
      echo "   ${GREEN}✓${RESET} Telegram chat_id: $OPT_TG_CHAT"
      ;;

    webhook)
      local wh="$OPT_WEBHOOK"
      if [ "$INTERACTIVE" = "true" ]; then
        while true; do
          prompt_input "Webhook URL (https://...)" "$wh" wh
          if echo "$wh" | grep -q "^https://"; then
            break
          else
            echo "   ${RED}❌ https:// 로 시작해야 합니다${RESET}"
          fi
        done
      else
        if [ -z "$wh" ] || ! echo "$wh" | grep -q "^https://"; then
          echo "${RED}❌ 유효한 Webhook URL 필요: --webhook https://...${RESET}" >&2
          exit 1
        fi
      fi
      OPT_WEBHOOK="$wh"
      echo "   ${GREEN}✓${RESET} Webhook URL: ${wh:0:40}..."
      ;;
  esac
}

# ── Step 4: 분석 기간 ────────────────────────────────────────
step_days() {
  echo ""
  echo "${BOLD}4. 분석 기간 (일수)${RESET}"
  echo "   ${DIM}최근 몇 일치 세션을 분석할지 (범위: 1-90)${RESET}"

  local d="$OPT_DAYS"
  if [ "$INTERACTIVE" = "true" ]; then
    while true; do
      prompt_input "분석 기간 (days)" "$d" d
      if validate_days "$d"; then
        break
      else
        echo "   ${RED}❌ 1-90 사이의 정수를 입력하세요${RESET}"
        d="$OPT_DAYS"
      fi
    done
  else
    if ! validate_days "$d"; then
      echo "${RED}❌ 분석 기간이 유효하지 않습니다: $d (1-90 필요)${RESET}" >&2
      exit 1
    fi
  fi
  OPT_DAYS="$d"
  echo "   ${GREEN}✓${RESET} 분석 기간: ${OPT_DAYS}일"
}

# ── Step 5: 최대 세션 수 ─────────────────────────────────────
step_max_sessions() {
  echo ""
  echo "${BOLD}5. 최대 세션 수${RESET}"
  echo "   ${DIM}한 번에 분석할 최대 세션 수 (범위: 1-200)${RESET}"

  local m="$OPT_MAX_SESSIONS"
  if [ "$INTERACTIVE" = "true" ]; then
    while true; do
      prompt_input "최대 세션 수 (max_sessions)" "$m" m
      if validate_max_sessions "$m"; then
        break
      else
        echo "   ${RED}❌ 1-200 사이의 정수를 입력하세요${RESET}"
        m="$OPT_MAX_SESSIONS"
      fi
    done
  else
    if ! validate_max_sessions "$m"; then
      echo "${RED}❌ 최대 세션 수가 유효하지 않습니다: $m (1-200 필요)${RESET}" >&2
      exit 1
    fi
  fi
  OPT_MAX_SESSIONS="$m"
  echo "   ${GREEN}✓${RESET} 최대 세션: ${OPT_MAX_SESSIONS}개"
}

# ── Step 6: 주요 언어 ────────────────────────────────────────
step_lang() {
  echo ""
  echo "${BOLD}6. 주요 언어${RESET}"
  echo "   ${DIM}ko = 한국어만 | en = 영어만 | auto = 자동 감지 (권장)${RESET}"

  local l="$OPT_LANG"
  if [ "$INTERACTIVE" = "true" ]; then
    while true; do
      prompt_input "언어 (ko/en/auto)" "$l" l
      l="$(echo "$l" | tr '[:upper:]' '[:lower:]')"
      if validate_lang "$l"; then
        break
      else
        echo "   ${RED}❌ ko, en, auto 중 하나를 입력하세요${RESET}"
        l="$OPT_LANG"
      fi
    done
  else
    l="$(echo "$l" | tr '[:upper:]' '[:lower:]')"
    if ! validate_lang "$l"; then
      echo "${RED}❌ 언어가 유효하지 않습니다: $l (ko/en/auto 필요)${RESET}" >&2
      exit 1
    fi
  fi
  OPT_LANG="$l"
  echo "   ${GREEN}✓${RESET} 언어: $OPT_LANG"
}

# ── config.yaml 생성 ─────────────────────────────────────────
write_config() {
  echo ""
  echo "${BOLD}설정 파일 저장 중...${RESET}"

  # 기존 파일 백업
  if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "${CONFIG_FILE}.bak.wizard" 2>/dev/null && \
      echo "   ${DIM}백업: ${CONFIG_FILE}.bak.wizard${RESET}"
  fi

  # auto_detect 설정
  local auto_detect="true"
  if [ "$OPT_LANG" = "ko" ] || [ "$OPT_LANG" = "en" ]; then
    auto_detect="false"
  fi

  # 언어별 패턴 필터 (lang=en이면 ko 패턴 축소)
  local ko_patterns en_patterns
  if [ "$OPT_LANG" = "en" ]; then
    ko_patterns='      []'
  else
    ko_patterns='      - "확인중"
      - "다시"
      - "아까"
      - "반복"
      - "기억"
      - "말했잖아"
      - "했잖아"
      - "이미 말했"
      - "계속"
      - "물어보지 말고"
      - "전부 다 해줘"
      - "왜 또"
      - "몇 번"
      - "또?"
      - "저번에도"
      - "왜 자꾸"
      - "또 그러네"
      - "안 되잖아"'
  fi

  if [ "$OPT_LANG" = "ko" ]; then
    en_patterns='      []'
  else
    en_patterns='      - "you forgot"
      - "again?"
      - "same mistake"
      - "stop doing that"
      - "how many times"
      - "wrong again"
      - "you already"
      - "I told you"
      - "keep doing"
      - "still broken"
      - "not what I asked"
      - "try again"
      - "that'"'"'s not right"
      - "still not working"
      - "told you"
      - "as I said"'
  fi

  # Discord 채널 설정 (플랫폼별)
  local discord_ch=""
  [ "$OPT_PLATFORM" = "discord" ] && discord_ch="$OPT_CHANNEL"

  # Slack webhook
  local slack_webhook=""
  [ "$OPT_PLATFORM" = "slack" ] && slack_webhook="$OPT_WEBHOOK"

  # Telegram
  local tg_token="" tg_chat=""
  [ "$OPT_PLATFORM" = "telegram" ] && tg_token="$OPT_TG_TOKEN" && tg_chat="$OPT_TG_CHAT"

  # Webhook
  local webhook_url=""
  [ "$OPT_PLATFORM" = "webhook" ] && webhook_url="$OPT_WEBHOOK"

  cat > "$CONFIG_FILE" << YAML_EOF
# ============================================================
# self-evolving-agent 설정 파일
# Generated by setup-wizard.sh on $(date '+%Y-%m-%d %H:%M:%S')
# 이 파일을 수정하면 스킬 동작이 바뀝니다.
# 재시작 없이 다음 크론 실행 시 자동 반영됩니다.
# ============================================================

# ── 분석 설정 ──────────────────────────────────────────────
analysis:
  # 최근 몇 일치 세션을 분석할지 (기본: 7일)
  days: ${OPT_DAYS}

  # 한 번에 분석할 최대 세션 수
  max_sessions: ${OPT_MAX_SESSIONS}

  # 분석 대상 에이전트 목록 (빈 배열 = 전체)
  agent_filter: []

  # 불만 패턴 키워드 (한국어/영어 분리 구조)
  complaint_patterns:
    ko:
${ko_patterns}
    en:
${en_patterns}
    auto_detect: ${auto_detect}

  # AGENTS.md 위반 패턴 (정규식)
  violation_patterns:
    - pattern: "git (?:pull|push|fetch)"
      rule: "git 작업은 git-sync.sh 사용 필수"
      severity: "high"
    - pattern: "(?:추가로|그리고\n|또한\n)"
      rule: "메시지 단편화 금지"
      severity: "low"
      min_hits: 5

  # 에러 로그 분석 대상 파일
  log_files:
    - "cron-catchup.log"
    - "heartbeat-cron.log"
    - "context-monitor.log"
    - "metrics-cron.log"

  # .learnings/ 경로
  learnings_paths:
    - "openclaw/.learnings"
    - ".openclaw/.learnings"

  # MEMORY.md 분석 포함 여부
  include_memory_md: true

# ── 제안 설정 ──────────────────────────────────────────────
proposals:
  complaint_min_hits: 2
  repeat_request_min: 3
  save_dir: "data/proposals"
  rejection_log: "data/rejected-proposals.json"
  expire_days: 30

# ── 크론 설정 ──────────────────────────────────────────────
cron:
  schedule: "${OPT_SCHEDULE}"
  model: "anthropic/claude-sonnet-4-5"
  discord_channel: "${discord_ch}"
  agent_id: "opus"

# ── 출력 설정 ──────────────────────────────────────────────
output:
  analysis_json: "/tmp/self-evolving-analysis.json"
  verbose: true
  max_message_length: 3500

# ── 배달 설정 ──────────────────────────────────────────────
delivery:
  platform: "${OPT_PLATFORM}"

  discord:
    channel_id: "${discord_ch}"

  slack:
    webhook_url: "${slack_webhook}"

  telegram:
    bot_token: "${tg_token}"
    chat_id: "${tg_chat}"

  webhook:
    url: "${webhook_url}"
    method: "POST"
    headers:
      Content-Type: "application/json"
YAML_EOF

  local write_status=$?
  if [ $write_status -eq 0 ]; then
    echo "   ${GREEN}✅ Config 저장: $CONFIG_FILE${RESET}"
  else
    echo "   ${RED}❌ Config 저장 실패${RESET}" >&2
    return 1
  fi
}

# ── 크론 등록 ────────────────────────────────────────────────
step_cron() {
  if [ "$OPT_NO_CRON" = "true" ]; then
    echo ""
    echo "   ${DIM}크론 등록 생략 (--no-cron)${RESET}"
    return 0
  fi

  echo ""
  echo "${BOLD}크론 등록${RESET}"
  echo "   ${DIM}스케줄: $OPT_SCHEDULE (Asia/Seoul)${RESET}"

  local register_cron=true
  if [ "$INTERACTIVE" = "true" ] && [ "$OPT_YES" != "true" ]; then
    if ! prompt_yesno "   크론 자동 등록하겠습니까?" "y"; then
      register_cron=false
    fi
  fi

  if [ "$register_cron" = "true" ]; then
    local register_script="$SCRIPT_DIR/register-cron.sh"
    if [ -f "$register_script" ]; then
      SEA_CONFIG="$CONFIG_FILE" bash "$register_script" 2>&1 | \
        sed 's/^/   /' || true
    else
      echo "   ${YELLOW}⚠️  register-cron.sh 없음: $register_script${RESET}"
      echo "   ${DIM}수동 등록: bash $register_script${RESET}"
    fi
  else
    echo "   ${DIM}수동 등록: bash $SCRIPT_DIR/register-cron.sh${RESET}"
  fi
}

# ── 검증 실행 ────────────────────────────────────────────────
step_validate() {
  echo ""
  echo "${BOLD}설정 검증 중...${RESET}"

  local validate_script="$SCRIPT_DIR/validate-config.sh"
  if [ -f "$validate_script" ]; then
    SEA_CONFIG="$CONFIG_FILE" bash "$validate_script" 2>&1 | sed 's/^/   /' || true
  else
    echo "   ${DIM}validate-config.sh 없음 — 검증 건너뜀${RESET}"
  fi
}

# ── 완료 메시지 ──────────────────────────────────────────────
print_done() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "  ${GREEN}${BOLD}✅ 설정 완료!${RESET}"
  echo ""
  echo "  다음 단계:"
  echo "  ${CYAN}  bash $SKILL_DIR/scripts/v4/orchestrator.sh${RESET}  # 즉시 실행"
  echo "  ${CYAN}  bash $SCRIPT_DIR/validate-config.sh${RESET}         # 설정 재검증"
  if [ "$OPT_NO_CRON" != "true" ]; then
    echo "  ${CYAN}  bash $SCRIPT_DIR/register-cron.sh --update${RESET}  # 크론 업데이트"
  fi
  echo ""
  echo "  ${DIM}설정 파일: $CONFIG_FILE${RESET}"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ── 메인 ────────────────────────────────────────────────────
main() {
  parse_args "$@"

  if [ "$INTERACTIVE" = "true" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "${BOLD}  🧠 Self-Evolving Agent — Setup Wizard${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  설정 파일을 생성합니다. Enter로 기본값을 사용하세요."
    echo "  언제든지 Ctrl+C로 취소할 수 있습니다."
  else
    echo "🧠 Self-Evolving Agent — 비대화형 설정"
  fi

  step_workspace
  step_platform
  step_credentials
  step_days
  step_max_sessions
  step_lang

  echo ""
  echo "${BOLD}설정 요약${RESET}"
  echo "   워크스페이스: $OPT_WORKSPACE"
  echo "   플랫폼:       $OPT_PLATFORM"
  case "$OPT_PLATFORM" in
    discord)  echo "   채널 ID:      $OPT_CHANNEL" ;;
    slack)    echo "   Webhook URL:  ${OPT_WEBHOOK:0:40}..." ;;
    telegram) echo "   Bot Token:    ...${OPT_TG_TOKEN: -8} | Chat ID: $OPT_TG_CHAT" ;;
    webhook)  echo "   Webhook URL:  ${OPT_WEBHOOK:0:40}..." ;;
  esac
  echo "   분석 기간:    ${OPT_DAYS}일"
  echo "   최대 세션:    ${OPT_MAX_SESSIONS}개"
  echo "   언어:         $OPT_LANG"
  echo "   크론 스케줄:  $OPT_SCHEDULE"

  local proceed=true
  if [ "$INTERACTIVE" = "true" ] && [ "$OPT_YES" != "true" ]; then
    echo ""
    if ! prompt_yesno "위 설정으로 config.yaml을 저장하겠습니까?" "y"; then
      echo ""
      echo "취소되었습니다."
      exit 1
    fi
  fi

  write_config || exit 1
  step_cron
  step_validate
  print_done
}

main "$@"
