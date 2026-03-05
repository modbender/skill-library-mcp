#!/bin/bash
set -euo pipefail

# Emergency Recovery Monitor - Discord 알림
# emergency-recovery 로그에서 실패 케이스 감지 → Discord 알림

# ============================================
# Configuration (Override via environment)
# ============================================
LOG_DIR="${OPENCLAW_MEMORY_DIR:-$HOME/openclaw/memory}"
ALERT_SENT_FILE="$LOG_DIR/.emergency-alert-sent"
ALERT_WINDOW_MINUTES="${EMERGENCY_ALERT_WINDOW:-30}"

# Create log directory if not exists
mkdir -p "$LOG_DIR"
chmod 700 "$LOG_DIR" 2>/dev/null || true

# Load environment variables
if [ -f "$HOME/openclaw/.env" ]; then
  # shellcheck source=/dev/null
  source "$HOME/openclaw/.env"
elif [ -f "$HOME/.openclaw/.env" ]; then
  # shellcheck source=/dev/null
  source "$HOME/.openclaw/.env"
fi

# Discord webhook from environment variable (optional)
DISCORD_WEBHOOK="${DISCORD_WEBHOOK_URL:-}"

# Secure temp file
ALERT_TMP=$(mktemp -t emergency-alert.XXXXXX)
chmod 600 "$ALERT_TMP"

# Cleanup on exit
trap 'rm -f "$ALERT_TMP"' EXIT

# ============================================
# Functions
# ============================================

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

get_latest_recovery_log() {
  # Use find instead of ls (ShellCheck SC2012)
  find "$LOG_DIR" -name "emergency-recovery-*.log" -type f -print0 2>/dev/null | \
    xargs -0 ls -t 2>/dev/null | head -1
}

is_alert_already_sent() {
  local latest_log="$1"
  
  if [ ! -f "$ALERT_SENT_FILE" ]; then
    return 1
  fi
  
  local sent_log
  sent_log=$(cat "$ALERT_SENT_FILE" 2>/dev/null || echo "")
  
  [ "$sent_log" = "$latest_log" ]
}

mark_alert_sent() {
  local latest_log="$1"
  
  # Atomic write
  echo "$latest_log" > "$ALERT_SENT_FILE.tmp"
  mv "$ALERT_SENT_FILE.tmp" "$ALERT_SENT_FILE"
}

send_alert() {
  local latest_log="$1"
  local timestamp
  timestamp=$(basename "$latest_log" | sed 's/emergency-recovery-//;s/.log//')
  
  # Discord 알림 메시지 생성
  cat > "$ALERT_TMP" << EOF
🚨 **긴급: OpenClaw 자가복구 실패**

**시간:** $timestamp
**상태:**
- Level 1 (Watchdog) ❌
- Level 2 (Health Check) ❌  
- Level 3 (Claude Recovery) ❌

**수동 개입 필요합니다.**

**로그:**
- \`$latest_log\`
- \`$LOG_DIR/claude-session-$timestamp.log\`
- \`$LOG_DIR/emergency-recovery-report-$timestamp.md\` (Claude가 생성했을 경우)

**복구 시도:**
1. \`openclaw status\` 확인
2. \`~/.openclaw/logs/*.log\` 에러 확인
3. \`openclaw gateway restart\` 시도
4. 필요 시 \`openclaw gateway stop && sleep 5 && openclaw gateway start\`
EOF

  local alert_msg
  alert_msg=$(cat "$ALERT_TMP")
  
  # Discord 직접 호출 (webhook 있을 경우)
  if [ -n "$DISCORD_WEBHOOK" ]; then
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" \
      -X POST "$DISCORD_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{\"content\": \"$alert_msg\"}" \
      2>&1 || echo "000")
    
    if [ "$response_code" = "200" ] || [ "$response_code" = "204" ]; then
      log "✅ Discord notification sent (HTTP $response_code)"
    else
      log "⚠️ Discord notification failed (HTTP $response_code), falling back to stdout"
      cat "$ALERT_TMP"
    fi
  else
    # Webhook 없으면 stdout 출력 (크론이 message tool로 전달)
    log "INFO: DISCORD_WEBHOOK_URL not set, printing to stdout"
    cat "$ALERT_TMP"
  fi
}

# ============================================
# Main Logic
# ============================================

main() {
  # 최근 N분 내 emergency-recovery 로그 찾기
  local recent_logs
  recent_logs=$(find "$LOG_DIR" -name "emergency-recovery-*.log" -type f -mmin -"$ALERT_WINDOW_MINUTES" 2>/dev/null)

  if [ -z "$recent_logs" ]; then
    # 최근 emergency recovery 없음
    log "No recent emergency recovery logs found (last ${ALERT_WINDOW_MINUTES} minutes)"
    exit 0
  fi

  # 가장 최근 로그 확인
  local latest_log
  latest_log=$(get_latest_recovery_log)

  if [ -z "$latest_log" ] || [ ! -f "$latest_log" ]; then
    log "No valid emergency recovery logs found"
    exit 0
  fi

  # 이미 알림 보낸 로그인지 체크
  if is_alert_already_sent "$latest_log"; then
    log "Alert already sent for: $latest_log"
    exit 0
  fi

  # "MANUAL INTERVENTION REQUIRED" 패턴 검색
  if grep -q "MANUAL INTERVENTION REQUIRED" "$latest_log"; then
    log "Found failed recovery in: $latest_log"
    
    # 알림 전송
    send_alert "$latest_log"
    
    # 알림 보냄 기록
    mark_alert_sent "$latest_log"
    
    exit 0
  else
    log "No manual intervention required in: $latest_log"
  fi

  exit 0
}

# Run main function
main
