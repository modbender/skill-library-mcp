#!/bin/bash
set -euo pipefail

# OpenClaw Emergency Recovery v2.0.0 (Level 3 Self-Healing)
# - Recovery Documentation (persistent learnings)
# - Reasoning Logs (explainability)
# - Telegram Alert support
# - Enhanced Metrics

# ============================================
# Cleanup trap
# ============================================
cleanup() {
    local exit_code=$?
    if [ -n "${TMUX_SESSION:-}" ]; then
        tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true
    fi
    # v2.1: 공용 락 파일 삭제
    rm -f "/tmp/openclaw-emergency-recovery.lock" 2>/dev/null || true
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

# ============================================
# Configuration
# ============================================
RECOVERY_TIMEOUT="${EMERGENCY_RECOVERY_TIMEOUT:-1800}"
GATEWAY_URL="${OPENCLAW_GATEWAY_URL:-http://localhost:18789/}"
LOG_DIR="${OPENCLAW_MEMORY_DIR:-$HOME/openclaw/memory}"
CLAUDE_WORKSPACE_TRUST_TIMEOUT="${CLAUDE_WORKSPACE_TRUST_TIMEOUT:-10}"
CLAUDE_STARTUP_WAIT="${CLAUDE_STARTUP_WAIT:-5}"
WORKSPACE_TRUST_CONFIRM_WAIT="${WORKSPACE_TRUST_CONFIRM_WAIT:-3}"

TIMESTAMP=$(date +%Y-%m-%d-%H%M)
LOG_FILE="$LOG_DIR/emergency-recovery-$TIMESTAMP.log"
REPORT_FILE="$LOG_DIR/emergency-recovery-report-$TIMESTAMP.md"
SESSION_LOG="$LOG_DIR/claude-session-$TIMESTAMP.log"
REASONING_LOG="$LOG_DIR/claude-reasoning-$TIMESTAMP.md"
TMUX_SESSION="emergency_recovery_$TIMESTAMP"

# NEW: Persistent learning repository
LEARNING_REPO="$LOG_DIR/recovery-learnings.md"

# Create log directory
mkdir -p "$LOG_DIR"
chmod 700 "$LOG_DIR" 2>/dev/null || true

touch "$SESSION_LOG"
chmod 600 "$SESSION_LOG"

# v2.1: 공용 락 파일 (Watchdog와 공유)
LOCKFILE="/tmp/openclaw-emergency-recovery.lock"
METRICS_FILE="$LOG_DIR/.emergency-recovery-metrics.json"

# Load environment variables (v3.1: improved path detection)
if [ -f "$HOME/.openclaw/.env" ]; then
  # shellcheck source=/dev/null
  source "$HOME/.openclaw/.env"
elif [ -f "$HOME/openclaw/.env" ]; then
  # shellcheck source=/dev/null
  source "$HOME/openclaw/.env"
fi

# Notification webhooks (optional - script continues without them)
DISCORD_WEBHOOK_URL="${DISCORD_WEBHOOK_URL:-}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

# Log notification status
if [ -z "$DISCORD_WEBHOOK_URL" ] && [ -z "$TELEGRAM_BOT_TOKEN" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: No notification webhooks configured. Recovery will proceed silently." | tee -a "$LOG_FILE"
fi

# ============================================
# Functions
# ============================================

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_discord_notification() {
  local message="$1"
  if [ -n "$DISCORD_WEBHOOK_URL" ]; then
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" \
      -X POST "$DISCORD_WEBHOOK_URL" \
      -H "Content-Type: application/json" \
      -d "{\"content\": \"$message\"}" \
      2>&1 || echo "000")
    
    if [ "$response_code" = "200" ] || [ "$response_code" = "204" ]; then
      log "✅ Discord notification sent (HTTP $response_code)"
    else
      log "⚠️ Discord notification failed (HTTP $response_code)"
    fi
  fi
}

send_telegram_notification() {
  local message="$1"
  if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" \
      -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
      -H "Content-Type: application/json" \
      -d "{\"chat_id\": \"$TELEGRAM_CHAT_ID\", \"text\": \"$message\", \"parse_mode\": \"Markdown\"}" \
      2>&1 || echo "000")
    
    if [ "$response_code" = "200" ]; then
      log "✅ Telegram notification sent (HTTP $response_code)"
    else
      log "⚠️ Telegram notification failed (HTTP $response_code)"
    fi
  fi
}

send_notification() {
  local message="$1"
  send_discord_notification "$message"
  send_telegram_notification "$message"
}

check_dependencies() {
  local missing_deps=()
  
  if ! command -v tmux &> /dev/null; then
    missing_deps+=("tmux")
  fi
  
  # v2.1: 절대 경로 사용 (LaunchAgent PATH 문제 해결)
  CLAUDE_BIN="/opt/homebrew/bin/claude"
  if [[ ! -x "$CLAUDE_BIN" ]]; then
    missing_deps+=("claude (not found at $CLAUDE_BIN)")
  fi
  
  if [ ${#missing_deps[@]} -gt 0 ]; then
    log "❌ Missing dependencies: ${missing_deps[*]}"
    send_notification "🚨 **Level 3 Emergency Recovery 실패**\n\n필수 의존성이 설치되지 않았습니다:\n- ${missing_deps[*]}\n\n설치 방법:\n\`\`\`bash\nbrew install ${missing_deps[*]}\n\`\`\`"
    return 1
  fi
  
  log "✅ Dependencies check passed"
  return 0
}

wait_for_claude_prompt() {
  local session="$1"
  local timeout="$2"
  
  log "Waiting for Claude workspace trust prompt (timeout: ${timeout}s)..."
  
  for _ in $(seq 1 "$timeout"); do
    local output
    output=$(tmux capture-pane -t "$session" -p 2>/dev/null || echo "")
    
    if echo "$output" | grep -q "trust this workspace"; then
      log "✅ Claude workspace trust prompt detected"
      return 0
    fi
    
    sleep 1
  done
  
  log "⚠️ Claude workspace trust prompt not detected after ${timeout}s"
  return 1
}

capture_tmux_session() {
  local session="$1"
  local output_file="$2"
  
  if tmux capture-pane -t "$session" -p > "$output_file" 2>/dev/null; then
    log "✅ tmux session captured: $output_file"
    return 0
  else
    log "⚠️ Failed to capture tmux session"
    return 1
  fi
}

check_claude_quota() {
  local session_log="$1"
  
  if grep -qE "rate limit|quota exceeded|429|too many requests" "$session_log"; then
    log "⚠️ Claude API rate limited or quota exceeded"
    return 1
  fi
  
  return 0
}

rotate_old_logs() {
  local deleted_count
  deleted_count=$(find "$LOG_DIR" -name "emergency-recovery-*.log" -mtime +14 -delete -print 2>/dev/null | wc -l)
  deleted_count=$((deleted_count + $(find "$LOG_DIR" -name "claude-session-*.log" -mtime +14 -delete -print 2>/dev/null | wc -l)))
  deleted_count=$((deleted_count + $(find "$LOG_DIR" -name "claude-reasoning-*.md" -mtime +14 -delete -print 2>/dev/null | wc -l)))
  
  if [ "$deleted_count" -gt 0 ]; then
    log "Rotated $deleted_count old log files"
  fi
}

record_metric() {
  local metric_name="$1"
  local result="$2"
  local duration="$3"
  local symptom="${4:-unknown}"
  local root_cause="${5:-unknown}"
  local timestamp
  timestamp=$(date +%s)
  
  # Enhanced metrics with symptom and root cause tracking
  echo "{\"timestamp\":$timestamp,\"metric\":\"$metric_name\",\"result\":\"$result\",\"duration\":$duration,\"symptom\":\"$symptom\",\"root_cause\":\"$root_cause\"}" >> "$METRICS_FILE"
}

cleanup_tmux_session() {
  local session="$1"
  
  if tmux has-session -t "$session" 2>/dev/null; then
    log "Terminating tmux session: $session"
    tmux kill-session -t "$session" 2>/dev/null || true
  fi
}

extract_learning() {
  local report_file="$1"
  local reasoning_file="$2"
  
  # Extract key learning from Claude's report and reasoning
  if [ -f "$report_file" ]; then
    log "Extracting learning from recovery report and reasoning log..."
    
    # Append to persistent learning repository
    {
      echo ""
      echo "## $(date '+%Y-%m-%d %H:%M') — Recovery Learning"
      echo ""
      echo "### Symptom"
      grep -A 5 "Symptom\|Problem\|Issue" "$report_file" | head -10 || echo "- Gateway timeout"
      echo ""
      echo "### Root Cause"
      grep -A 5 "Root Cause\|Cause\|Reason" "$report_file" | head -10 || echo "- Unknown"
      echo ""
      echo "### Solution"
      grep -A 10 "Solution\|Fix\|Resolution" "$report_file" | head -15 || echo "- See report: $report_file"
      echo ""
      echo "### Prevention"
      grep -A 5 "Prevention\|Future\|Recommendation" "$report_file" | head -10 || echo "- TBD"
      echo ""
      
      # NEW: Extract reasoning from Claude's reasoning log (v2.0.1)
      if [ -f "$reasoning_file" ]; then
        echo "### Claude's Reasoning Process"
        echo ""
        echo "**Decision Making:**"
        grep -A 5 "Decision Making\|Decision\|Choice" "$reasoning_file" | head -10 || echo "- See full reasoning: $reasoning_file"
        echo ""
        echo "**Lessons Learned:**"
        grep -A 5 "Lessons Learned\|Lessons\|Insights" "$reasoning_file" | head -10 || echo "- See full reasoning: $reasoning_file"
        echo ""
      else
        echo "### Claude's Reasoning Process"
        echo "- Reasoning log not available: $reasoning_file"
        echo ""
      fi
      
      echo "---"
    } >> "$LEARNING_REPO"
    
    log "✅ Learning appended to $LEARNING_REPO (including reasoning)"
  else
    log "⚠️ No report file found, skipping learning extraction"
  fi
}

# ============================================
# Main Recovery Logic
# ============================================

main() {
  local start_time
  start_time=$(date +%s)
  
  log "=== Emergency Recovery v2.0 Started (PID: $$) ==="
  
  # 0. Log rotation
  rotate_old_logs
  
  # 1. Check dependencies
  if ! check_dependencies; then
    log "🚨 Cannot proceed without required dependencies"
    record_metric "emergency_recovery" "dependency_failed" 0
    exit 1
  fi
  
  # 2. Claude Code PTY 세션 시작
  log "Starting Claude Code session in tmux..."
  
  # v2.1: 절대 경로 사용
  if ! tmux new-session -d -s "$TMUX_SESSION" "/opt/homebrew/bin/claude" 2>> "$LOG_FILE"; then
    log "❌ Failed to start tmux session"
    send_notification "🚨 **Level 3 실패**\n\ntmux 세션 시작 실패.\n\n수동 개입 필요:\n\`$LOG_FILE\`"
    record_metric "emergency_recovery" "tmux_failed" 0
    exit 1
  fi
  
  sleep "$CLAUDE_STARTUP_WAIT"
  
  # 3. 워크스페이스 신뢰
  if wait_for_claude_prompt "$TMUX_SESSION" "$CLAUDE_WORKSPACE_TRUST_TIMEOUT"; then
    log "Trusting workspace..."
    tmux send-keys -t "$TMUX_SESSION" "" C-m
    sleep "$WORKSPACE_TRUST_CONFIRM_WAIT"
  else
    log "⚠️ Proceeding without workspace trust confirmation"
  fi
  
  # 4. 긴급 복구 명령 전송 (v2.0 enhanced instructions)
  log "Sending emergency recovery command to Claude (v2.0 with reasoning + documentation)..."
  
  local recovery_command
  recovery_command="OpenClaw 게이트웨이가 5분간 재시작했으나 복구되지 않았습니다. 긴급 진단 및 복구를 시작하세요.

**작업 순서:**
1. \`openclaw status\` 체크
2. 로그 분석 (~/.openclaw/logs/*.log)
3. 설정 검증 (~/.openclaw/openclaw.json)
4. 포트 충돌 체크 (\`lsof -i :18789\`)
5. 의존성 체크 (\`npm list\`, \`node --version\`)
6. 복구 시도 (설정 수정, 프로세스 재시작)

**출력 형식:**
두 개의 파일을 생성하세요:

1. **$REPORT_FILE** (Recovery Report):
\`\`\`markdown
## Recovery Report — $(date '+%Y-%m-%d %H:%M')

### Symptom
- [문제 증상을 명확하게 기술]

### Root Cause
- [근본 원인 분석]

### Solution Applied
- [적용한 해결책]

### Result
- [복구 결과: 성공/실패]

### Prevention
- [향후 재발 방지 방법]
\`\`\`

2. **$REASONING_LOG** (Reasoning Process):
\`\`\`markdown
## Claude Reasoning Log — $(date '+%Y-%m-%d %H:%M')

### Initial Assessment
- [첫 판단]

### Hypothesis
- [가설들]

### Investigation
- [조사 과정]

### Decision Making
- [왜 이 해결책을 선택했는가]

### Lessons Learned
- [이번 복구에서 배운 것]
\`\`\`

**작업 제한시간:** ${RECOVERY_TIMEOUT}초
**목표:** Gateway가 $GATEWAY_URL 에서 HTTP 200 응답하도록 복구"
  
  if ! tmux send-keys -t "$TMUX_SESSION" "$recovery_command" C-m 2>> "$LOG_FILE"; then
    log "❌ Failed to send command to Claude"
    cleanup_tmux_session "$TMUX_SESSION"
    send_notification "🚨 **Level 3 실패**\n\nClaude 명령 전송 실패.\n\n수동 개입 필요:\n\`$LOG_FILE\`"
    record_metric "emergency_recovery" "command_failed" 0
    exit 1
  fi
  
  # 5. Claude 작업 대기
  log "Waiting for Claude to complete recovery (max ${RECOVERY_TIMEOUT}s)..."
  
  local poll_interval=30
  local elapsed=0
  local last_output=""
  local idle_count=0
  local max_idle=6
  
  while [ $elapsed -lt "$RECOVERY_TIMEOUT" ]; do
    sleep "$poll_interval"
    elapsed=$((elapsed + poll_interval))
    
    local current_output
    current_output=$(tmux capture-pane -t "$TMUX_SESSION" -p 2>/dev/null | tail -20 || echo "")
    
    if echo "$current_output" | grep -qiE "(recovery (completed|complete|finished)|task (completed|complete|finished)|wrote.*report|gateway.*restored|http 200|✅.*(success|recover|complete))"; then
      log "✅ Claude appears to have completed (detected completion signal)"
      break
    fi
    
    if [ "$current_output" = "$last_output" ]; then
      idle_count=$((idle_count + 1))
      if [ $idle_count -ge $max_idle ]; then
        log "⚠️ Claude idle for $((idle_count * poll_interval))s, assuming completion"
        break
      fi
    else
      idle_count=0
      last_output="$current_output"
    fi
    
    tmux capture-pane -t "$TMUX_SESSION" -p >> "$SESSION_LOG" 2>/dev/null || true
    echo "--- poll at ${elapsed}s ---" >> "$SESSION_LOG"
    
    log "... still working (${elapsed}s elapsed, idle: ${idle_count})"
  done
  
  if [ $elapsed -ge "$RECOVERY_TIMEOUT" ]; then
    log "⚠️ Recovery timeout reached (${RECOVERY_TIMEOUT}s)"
  else
    log "✅ Claude completed in ${elapsed}s (saved $((RECOVERY_TIMEOUT - elapsed))s)"
  fi
  
  # 6. tmux 세션 캡처
  log "Capturing Claude session output..."
  capture_tmux_session "$TMUX_SESSION" "$SESSION_LOG"
  
  # 7. Claude 할당량 체크
  local SUCCESS="unknown"
  
  if ! check_claude_quota "$SESSION_LOG"; then
    send_notification "⚠️ **Level 3 Emergency Recovery 실패**\n\nClaude API 할당량 소진 또는 속도 제한.\n\n다음 단계:\n1. Claude 할당량 확인: \`claude\` → \`/usage\`\n2. 수동 복구 시도\n\n세션 로그: \`$SESSION_LOG\`"
    SUCCESS="false"
  fi
  
  # 8. 결과 확인
  log "Checking recovery result..."
  
  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$GATEWAY_URL" 2>/dev/null || echo "000")
  
  if [ "$http_code" = "200" ] && [ "$SUCCESS" != "false" ]; then
    log "✅ Claude successfully recovered the gateway! (HTTP $http_code)"
    SUCCESS="true"
  else
    log "❌ Gateway still unhealthy after Claude recovery (HTTP $http_code)"
    SUCCESS="false"
  fi
  
  # 9. Extract learning (NEW in v2.0)
  extract_learning "$REPORT_FILE" "$REASONING_LOG"
  
  # 10. tmux 세션 종료
  cleanup_tmux_session "$TMUX_SESSION"
  
  # 11. Performance metrics (enhanced with symptom/cause tracking)
  local end_time
  end_time=$(date +%s)
  local total_time=$((end_time - start_time))
  
  # Extract symptom and root cause from report (if available)
  local symptom="unknown"
  local root_cause="unknown"
  if [ -f "$REPORT_FILE" ]; then
    symptom=$(grep -A 2 "### Symptom" "$REPORT_FILE" | tail -1 | sed 's/^- //' || echo "unknown")
    root_cause=$(grep -A 2 "### Root Cause" "$REPORT_FILE" | tail -1 | sed 's/^- //' || echo "unknown")
  fi
  
  record_metric "emergency_recovery" "$SUCCESS" "$total_time" "$symptom" "$root_cause"
  
  # 12. Discord/Telegram 알림 및 종료
  log "=== Emergency Recovery v2.0 Completed (${total_time}s) ==="
  
  if [ "$SUCCESS" = "true" ]; then
    log "✅ Sending success notification..."
    send_notification "✅ **Level 3 Emergency Recovery 성공!**\n\nGateway가 Claude에 의해 복구되었습니다.\n- 복구 시간: ${total_time}초\n- HTTP 상태: $http_code\n- 증상: $symptom\n- 근본 원인: $root_cause\n- 로그: \`$LOG_FILE\`\n- 복구 리포트: \`$REPORT_FILE\`\n- 추론 과정: \`$REASONING_LOG\`\n- 학습 누적: \`$LEARNING_REPO\`"
    exit 0
  else
    log "🚨 Sending failure notification..."

    local failure_msg
    failure_msg="🚨 **Level 3 Emergency Recovery 실패!**\n\n**모든 자동 복구 시스템이 실패했습니다:**\n- Level 1 (Watchdog): ❌\n- Level 2 (Health Check): ❌\n- Level 3 (Claude Recovery): ❌\n\n**수동 개입 필요**\n- HTTP 상태: $http_code\n- 복구 시간: ${total_time}초\n- 로그: \`$LOG_FILE\`\n- Claude 세션: \`$SESSION_LOG\`\n- 복구 리포트: \`$REPORT_FILE\`\n- 추론 과정: \`$REASONING_LOG\`"

    send_notification "$failure_msg"

    cat >> "$LOG_FILE" << EOF

=== MANUAL INTERVENTION REQUIRED ===
Level 1 (Watchdog) ❌
Level 2 (Health Check) ❌
Level 3 (Claude Recovery) ❌

수동 개입 필요합니다.
복구 시간: ${total_time}초
로그: $LOG_FILE
Claude 세션: $SESSION_LOG
복구 리포트: $REPORT_FILE
추론 과정: $REASONING_LOG
학습 저장소: $LEARNING_REPO
EOF

    exit 1
  fi
}

# Run main function
main
