#!/bin/bash
# Runtime Security Monitor for OpenClaw Skills
# Part of openclaw-defender - monitors skill execution in real-time
#
# Integration: Runtime protection only applies when the gateway (or your setup)
# calls this script at skill start/end and before network/file/command/RAG ops.
# If OpenClaw does not hook these yet, the runtime layer is dormant; you can
# still use kill-switch and analyze-security on manually logged events.

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
LOG_FILE="${OPENCLAW_LOGS:-$WORKSPACE/logs}/runtime-security.jsonl"
NW_WHITELIST_FILE="$WORKSPACE/.defender-network-whitelist"
SAFE_COMMANDS_FILE="$WORKSPACE/.defender-safe-commands"
RAG_ALLOWLIST_FILE="$WORKSPACE/.defender-rag-allowlist"
KILL_SWITCH_FILE="$WORKSPACE/.kill-switch"

mkdir -p "$(dirname "$LOG_FILE")"

# Structured logging (JSON Lines)
log_event() {
  local level="$1"
  local event_type="$2"
  local message="$3"
  local details="$4"
  
  local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  local event="{\"timestamp\":\"$timestamp\",\"level\":\"$level\",\"type\":\"$event_type\",\"message\":\"$message\""
  
  if [ -n "$details" ]; then
    event="$event,\"details\":$details"
  fi
  
  event="$event}"
  echo "$event" >> "$LOG_FILE"
  
  # Also print to stderr for immediate visibility
  echo "[$(date '+%H:%M:%S')] [$level] $event_type: $message" >&2
}

# Check if kill switch is active
check_kill_switch() {
  if [ -f "$KILL_SWITCH_FILE" ]; then
    log_event "CRITICAL" "kill_switch_active" "Emergency shutdown active - blocking all operations" "{}"
    echo "🚨 KILL SWITCH ACTIVE - All operations blocked"
    echo "To disable: rm $KILL_SWITCH_FILE"
    exit 1
  fi
}

# Activate kill switch
activate_kill_switch() {
  local reason="$1"
  echo "ACTIVATED: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" > "$KILL_SWITCH_FILE"
  echo "REASON: $reason" >> "$KILL_SWITCH_FILE"
  log_event "CRITICAL" "kill_switch_activated" "$reason" "{}"
  
  # Log security incident
  cat >> "$WORKSPACE/memory/security-incidents.md" << EOF

## 🚨 KILL SWITCH ACTIVATED
**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Reason:** $reason
**Action:** All skill operations blocked until manual review
**Next Steps:**
1. Investigate: cat $LOG_FILE | tail -100
2. Review recent skill activity
3. Check for unauthorized changes
4. Rotate credentials if compromised
5. Disable kill switch: rm $KILL_SWITCH_FILE

EOF
}

# Monitor network requests
monitor_network() {
  local url="$1"
  local skill="$2"
  
  # Whitelist: built-in + optional workspace file
  local whitelist=(
    "api.github.com"
    "npmjs.com"
    "pypi.org"
    "archive.org"
    "openclaw.ai"
    "coinglass.com"
    "alternative.me"
  )
  if [ -f "$NW_WHITELIST_FILE" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
      line="${line%%#*}"
      line="$(echo "$line" | tr -d '[:space:]')"
      [ -n "$line" ] && whitelist+=("$line")
    done < "$NW_WHITELIST_FILE"
  fi
  
  # Check whitelist
  for domain in "${whitelist[@]}"; do
    if echo "$url" | grep -q "$domain"; then
      log_event "INFO" "network_request" "Whitelisted request: $url" "{\"skill\":\"$skill\",\"url\":\"$url\"}"
      return 0
    fi
  done
  
  # Block suspicious patterns
  if echo "$url" | grep -qE "(91\.92\.242\.30|glot\.io|pastebin\.|raw\.githubusercontent\.com/[^/]+/[^/]+/[a-f0-9]{40})"; then
    log_event "CRITICAL" "network_blocked" "Malicious URL blocked: $url" "{\"skill\":\"$skill\",\"url\":\"$url\"}"
    activate_kill_switch "Malicious network request detected: $url"
    return 1
  fi
  
  # Warn on unknown external requests
  log_event "WARN" "network_request" "Unknown external request (review): $url" "{\"skill\":\"$skill\",\"url\":\"$url\"}"
  return 0
}

# Monitor file access
monitor_file_access() {
  local file="$1"
  local operation="$2"  # read, write, delete
  local skill="$3"
  
  # Block credential files
  local blocked_patterns=(
    "\.env"
    "\.agent-private-key-SECURE"
    "\.ssh/"
    "\.aws/"
    "\.config/gcloud"
    "secret"
    "token"
    "password"
  )
  
  for pattern in "${blocked_patterns[@]}"; do
    if echo "$file" | grep -qiE "$pattern"; then
      log_event "CRITICAL" "file_access_blocked" "Credential access attempt blocked: $file" "{\"skill\":\"$skill\",\"file\":\"$file\",\"operation\":\"$operation\"}"
      activate_kill_switch "Credential file access attempt: $file"
      return 1
    fi
  done
  
  # Block writes to critical files (including defender config and integrity baselines)
  if [ "$operation" = "write" ] || [ "$operation" = "delete" ]; then
    local critical_files=(
      "SOUL.md"
      "MEMORY.md"
      "IDENTITY.md"
      "USER.md"
      "AGENTS.md"
      ".defender-network-whitelist"
      ".defender-safe-commands"
      ".defender-rag-allowlist"
      ".integrity"
      ".integrity-manifest.sha256"
    )
    
    for critical in "${critical_files[@]}"; do
      if echo "$file" | grep -q "$critical"; then
        log_event "CRITICAL" "file_write_blocked" "Critical file modification blocked: $file" "{\"skill\":\"$skill\",\"file\":\"$file\",\"operation\":\"$operation\"}"
        activate_kill_switch "Unauthorized modification attempt: $file"
        return 1
      fi
    done
  fi
  
  log_event "INFO" "file_access" "File access: $operation $file" "{\"skill\":\"$skill\",\"file\":\"$file\",\"operation\":\"$operation\"}"
  return 0
}

# Monitor command execution
monitor_command() {
  local command="$1"
  local skill="$2"
  
  # Block dangerous commands
  local dangerous=(
    "rm -rf"
    "dd if="
    "mkfs"
    "> /dev/sd"
    "curl.*|.*bash"
    "wget.*|.*sh"
    "nc -l"
    "ncat.*-e"
    "base64 -d.*bash"
  )
  
  for pattern in "${dangerous[@]}"; do
    if echo "$command" | grep -qE "$pattern"; then
      log_event "CRITICAL" "command_blocked" "Dangerous command blocked: $command" "{\"skill\":\"$skill\",\"command\":\"$command\"}"
      activate_kill_switch "Dangerous command execution attempt: $command"
      return 1
    fi
  done
  
  # Whitelist: built-in safe read-only commands + optional workspace file
  local safe_commands=(
    "ls" "cat" "grep" "find" "head" "tail"
    "echo" "date" "pwd" "whoami"
    "git status" "git log" "git diff"
  )
  if [ -f "$SAFE_COMMANDS_FILE" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
      line="${line%%#*}"
      line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
      [ -n "$line" ] && safe_commands+=("$line")
    done < "$SAFE_COMMANDS_FILE"
  fi
  
  for safe in "${safe_commands[@]}"; do
    if echo "$command" | grep -q "^$safe"; then
      log_event "DEBUG" "command_executed" "Safe command: $command" "{\"skill\":\"$skill\",\"command\":\"$command\"}"
      return 0
    fi
  done
  
  # Warn on unknown commands
  log_event "WARN" "command_executed" "Unknown command (review): $command" "{\"skill\":\"$skill\",\"command\":\"$command\"}"
  return 0
}

# Sanitize output (prevent data exfiltration)
sanitize_output() {
  local output="$1"
  
  # Redact sensitive patterns
  output=$(echo "$output" | sed -E 's/0x[a-fA-F0-9]{64}/[REDACTED_KEY]/g')
  output=$(echo "$output" | sed -E 's/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}/[EMAIL]/g')
  output=$(echo "$output" | sed -E 's/\b[0-9]{3}[-.]?[0-9]{3}[-.]?[0-9]{4}\b/[PHONE]/g')
  output=$(echo "$output" | sed -E 's/(secret|password|token|key)[:=]\s*[A-Za-z0-9+\/=]{10,}/\1=[REDACTED]/gi')
  
  # Remove suspicious external URLs (potential exfiltration)
  output=$(echo "$output" | sed -E 's|https?://[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}[^ ]*|[EXTERNAL_IP]|g')
  
  # Strip base64 blobs (> 100 chars)
  output=$(echo "$output" | sed -E 's/[A-Za-z0-9+\/]{100,}={0,2}/[BASE64_BLOB]/g')
  
  # Size limit (1MB)
  local max_size=$((1024 * 1024))
  if [ ${#output} -gt $max_size ]; then
    output="${output:0:$max_size}[...TRUNCATED]"
  fi
  
  echo "$output"
}

# Block RAG operations (unless operation matches allowlist)
block_rag() {
  local operation="$1"
  local skill="$2"
  
  # Allowlist: if operation matches a line in .defender-rag-allowlist, do not block
  if [ -f "$RAG_ALLOWLIST_FILE" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
      line="${line%%#*}"
      line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
      if [ -n "$line" ] && echo "$operation" | grep -qiF "$line"; then
        log_event "INFO" "rag_allowed" "RAG allowlist match: $operation" "{\"skill\":\"$skill\",\"operation\":\"$operation\"}"
        return 0
      fi
    done < "$RAG_ALLOWLIST_FILE"
  fi
  
  local rag_patterns=(
    "embedding"
    "vector_store"
    "chroma"
    "pinecone"
    "faiss"
    "retrieve"
    "semantic_search"
  )
  
  for pattern in "${rag_patterns[@]}"; do
    if echo "$operation" | grep -qi "$pattern"; then
      log_event "CRITICAL" "rag_blocked" "RAG operation blocked (EchoLeak/GeminiJack vector): $operation" "{\"skill\":\"$skill\",\"operation\":\"$operation\"}"
      activate_kill_switch "RAG operation attempted: $operation"
      return 1
    fi
  done
  
  return 0
}

# Detect collusion (multi-skill coordination).
# Only meaningful when the execution path calls runtime-monitor.sh start/end for each skill.
detect_collusion() {
  local skill="$1"
  
  # Check if multiple skills are active simultaneously
  local active_skills=$(grep -c '"type":"skill_execution_start"' "$LOG_FILE" 2>/dev/null || echo 0)
  local completed_skills=$(grep -c '"type":"skill_execution_end"' "$LOG_FILE" 2>/dev/null || echo 0)
  local concurrent=$((active_skills - completed_skills))
  
  if [ $concurrent -gt 3 ]; then
    log_event "WARN" "collusion_suspected" "Unusual concurrent skill execution: $concurrent active" "{\"skill\":\"$skill\",\"concurrent\":$concurrent}"
  fi
  
  # Check for cross-skill file modifications
  local recent_modifications=$(grep '"file_access"' "$LOG_FILE" | tail -10 | grep -c '"operation":"write"')
  if [ $recent_modifications -gt 5 ]; then
    log_event "WARN" "collusion_suspected" "High file modification rate across skills" "{\"skill\":\"$skill\",\"modifications\":$recent_modifications}"
  fi
}

# Main monitoring function (called by OpenClaw before skill execution)
monitor_skill_start() {
  local skill="$1"
  check_kill_switch
  log_event "INFO" "skill_execution_start" "Skill starting: $skill" "{\"skill\":\"$skill\"}"
  detect_collusion "$skill"
}

monitor_skill_end() {
  local skill="$1"
  local exit_code="$2"
  log_event "INFO" "skill_execution_end" "Skill completed: $skill (exit: $exit_code)" "{\"skill\":\"$skill\",\"exit_code\":$exit_code}"
}

# CLI interface
case "${1:-}" in
  start)
    monitor_skill_start "$2"
    ;;
  end)
    monitor_skill_end "$2" "$3"
    ;;
  check-network)
    monitor_network "$2" "$3"
    ;;
  check-file)
    monitor_file_access "$2" "$3" "$4"
    ;;
  check-command)
    monitor_command "$2" "$3"
    ;;
  check-rag)
    block_rag "$2" "$3"
    ;;
  sanitize)
    sanitize_output "$(cat)"
    ;;
  kill-switch)
    if [ "$2" = "activate" ]; then
      activate_kill_switch "${3:-Manual activation}"
    elif [ "$2" = "check" ]; then
      check_kill_switch
    elif [ "$2" = "disable" ]; then
      rm -f "$KILL_SWITCH_FILE"
      echo "Kill switch disabled"
    fi
    ;;
  *)
    echo "Usage: $0 {start|end|check-network|check-file|check-command|check-rag|sanitize|kill-switch} [args...]"
    echo ""
    echo "Commands:"
    echo "  start SKILL_NAME              - Log skill execution start"
    echo "  end SKILL_NAME EXIT_CODE      - Log skill execution end"
    echo "  check-network URL SKILL_NAME  - Validate network request"
    echo "  check-file FILE OP SKILL_NAME - Validate file access (read|write|delete)"
    echo "  check-command CMD SKILL_NAME  - Validate command execution"
    echo "  check-rag OP SKILL_NAME       - Block RAG operations"
    echo "  sanitize                      - Sanitize stdin output"
    echo "  kill-switch activate [reason] - Emergency shutdown"
    echo "  kill-switch check             - Check if active"
    echo "  kill-switch disable           - Disable kill switch"
    exit 1
    ;;
esac
