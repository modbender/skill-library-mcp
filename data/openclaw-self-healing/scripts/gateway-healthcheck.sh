#!/bin/bash
set -euo pipefail

# OpenClaw Gateway Health Check (Level 2 Self-Healing)
# HTTP 응답 검증 → 실패 시 재시작 → 5분 후 재검증 → 실패 시 Level 3 escalation

# ============================================
# Configuration (Override via environment)
# ============================================
GATEWAY_URL="${OPENCLAW_GATEWAY_URL:-http://localhost:18789/}"
MAX_RETRIES="${HEALTH_CHECK_MAX_RETRIES:-3}"
RETRY_DELAY="${HEALTH_CHECK_RETRY_DELAY:-30}"
ESCALATION_WAIT="${HEALTH_CHECK_ESCALATION_WAIT:-300}"
LOG_DIR="${OPENCLAW_MEMORY_DIR:-$HOME/openclaw/memory}"
LOG_FILE="$LOG_DIR/healthcheck-$(date +%Y-%m-%d).log"
HTTP_TIMEOUT="${HEALTH_CHECK_HTTP_TIMEOUT:-10}"

# Performance metrics
METRICS_FILE="$LOG_DIR/.healthcheck-metrics.json"

# Lock file로 중복 실행 방지
LOCKFILE=/tmp/openclaw-healthcheck.lock
if [ -f "$LOCKFILE" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Previous health check still running, skipping..."
  exit 0
fi
touch "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

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

# Validate webhook URL (optional, warning only)
if [ -z "$DISCORD_WEBHOOK" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: DISCORD_WEBHOOK_URL not set. Notifications disabled." | tee -a "$LOG_FILE"
fi

# ============================================
# Functions
# ============================================

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_discord_notification() {
  local message="$1"
  if [ -n "$DISCORD_WEBHOOK" ]; then
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" \
      -X POST "$DISCORD_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{\"content\": \"$message\"}" \
      2>&1)
    
    if [ "$response_code" = "200" ] || [ "$response_code" = "204" ]; then
      log "✅ Discord notification sent (HTTP $response_code)"
    else
      log "⚠️ Discord notification failed (HTTP $response_code)"
    fi
  fi
}

check_http() {
  local start_time
  start_time=$(date +%s)
  
  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time "$HTTP_TIMEOUT" \
    "$GATEWAY_URL" 2>/dev/null || echo "000")
  
  local end_time
  end_time=$(date +%s)
  local response_time=$((end_time - start_time))
  
  # Record metric
  record_metric "http_check" "$http_code" "$response_time"
  
  if [ "$http_code" = "200" ]; then
    log "HTTP check passed (${response_time}s)"
    return 0
  else
    log "HTTP check failed: HTTP $http_code (${response_time}s)"
    return 1
  fi
}

restart_gateway() {
  log "Restarting OpenClaw Gateway..."
  
  local start_time
  start_time=$(date +%s)
  
  if openclaw gateway restart >> "$LOG_FILE" 2>&1; then
    local end_time
    end_time=$(date +%s)
    local restart_time=$((end_time - start_time))
    
    log "Gateway restart completed (${restart_time}s)"
    record_metric "gateway_restart" "success" "$restart_time"
    
    sleep "$RETRY_DELAY"
    return 0
  else
    log "⚠️ Gateway restart command failed"
    record_metric "gateway_restart" "failed" 0
    return 1
  fi
}

rotate_old_logs() {
  # Delete logs older than 14 days
  local deleted_count
  deleted_count=$(find "$LOG_DIR" -name "healthcheck-*.log" -mtime +14 -delete -print 2>/dev/null | wc -l)
  
  if [ "$deleted_count" -gt 0 ]; then
    log "Rotated $deleted_count old log files"
  fi
}

record_metric() {
  local metric_name="$1"
  local result="$2"
  local duration="$3"
  local timestamp
  timestamp=$(date +%s)
  
  # Append to metrics file (JSON Lines format)
  echo "{\"timestamp\":$timestamp,\"metric\":\"$metric_name\",\"result\":\"$result\",\"duration\":$duration}" >> "$METRICS_FILE"
}

escalate_to_level3() {
  log "🚨 Still unhealthy after ${ESCALATION_WAIT}s, triggering emergency recovery..."

  # Discord 알림 (Level 3 시작)
  send_discord_notification "🚨 **Level 3 Emergency Recovery 시작**\n\n${ESCALATION_WAIT}초 대기 후에도 Gateway 복구 안 됨.\nClaude가 자동으로 진단 및 복구를 시도합니다.\n\n예상 소요 시간: 30분\n현재 시각: $(date '+%Y-%m-%d %H:%M:%S')"

  # v3.1: Updated to emergency-recovery-v2.sh
  local emergency_script="$HOME/.openclaw/skills/openclaw-self-healing/scripts/emergency-recovery-v2.sh"

  if [ -f "$emergency_script" ]; then
    bash "$emergency_script" &
    log "✅ Emergency recovery v2 started (background)"
  else
    log "❌ Emergency recovery script not found: $emergency_script"
    send_discord_notification "🚨 **Level 3 실행 실패**\n\nEmergency recovery script not found:\n\`$emergency_script\`\n\n수동 개입 필요."
  fi
}

# ============================================
# Main Logic
# ============================================

main() {
  log "=== Health Check Started (PID: $$) ==="

  # Log rotation (cleanup old logs)
  rotate_old_logs

  # HTTP 응답 체크
  if ! check_http; then
    log "⚠️ Gateway unhealthy (HTTP failed)"
    
    # 3번 재시도
    for i in $(seq 1 "$MAX_RETRIES"); do
      log "Retry $i/$MAX_RETRIES..."
      
      if restart_gateway && check_http; then
        log "✅ Recovery successful on retry $i"

        # Discord 알림 (복구 성공)
        send_discord_notification "✅ **Gateway 복구 성공**\n\nLevel 2 Health Check가 Gateway를 재시작하여 복구했습니다.\n- 재시도 횟수: $i/$MAX_RETRIES\n- 현재 시각: $(date '+%Y-%m-%d %H:%M:%S')"

        record_metric "recovery" "success" "$i"
        exit 0
      fi
    done
    
    log "❌ Recovery failed after $MAX_RETRIES retries"
    log "🚨 Escalating to Level 3 (Claude Emergency Recovery)..."
    record_metric "recovery" "failed" "$MAX_RETRIES"

    # Discord 알림 (Level 3로 escalation)
    send_discord_notification "⚠️ **Level 2 Health Check 실패**\n\nGateway를 ${MAX_RETRIES}회 재시작했으나 복구 실패.\n${ESCALATION_WAIT}초 후 Level 3 (Claude Emergency Recovery)로 escalation합니다.\n\n현재 시각: $(date '+%Y-%m-%d %H:%M:%S')"

    # 5분 대기 후 최종 검증
    sleep "$ESCALATION_WAIT"

    if ! check_http; then
      escalate_to_level3
    else
      log "✅ Gateway recovered during waiting period"

      # Discord 알림 (대기 중 복구됨)
      send_discord_notification "✅ **Gateway 자동 복구됨**\n\n${ESCALATION_WAIT}초 대기 중 Gateway가 스스로 복구되었습니다.\nLevel 3 Emergency Recovery는 실행하지 않습니다."
      
      record_metric "recovery" "self_healed" 0
    fi
  else
    log "✅ Gateway healthy"
    record_metric "health_check" "healthy" 0
  fi

  log "=== Health Check Completed ==="
}

# Run main function
main
