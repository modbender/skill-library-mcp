#!/bin/bash
# Security Event Analyzer - parses runtime-security.jsonl and detects patterns
# Part of openclaw-defender

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
LOG_FILE="${OPENCLAW_LOGS:-$WORKSPACE/logs}/runtime-security.jsonl"
REPORT_FILE="$WORKSPACE/memory/security-report-$(date +%Y-%m-%d).md"

if [ ! -f "$LOG_FILE" ]; then
  echo "No security log found: $LOG_FILE"
  exit 1
fi

echo "=== OpenClaw Defender: Security Event Analysis ==="
echo "Log: $LOG_FILE"
echo "Report: $REPORT_FILE"
echo ""

# Count events by level
CRITICAL=$(grep -c '"level":"CRITICAL"' "$LOG_FILE")
WARN=$(grep -c '"level":"WARN"' "$LOG_FILE")
INFO=$(grep -c '"level":"INFO"' "$LOG_FILE")

echo "Event Summary:"
echo "  🚨 CRITICAL: $CRITICAL"
echo "  ⚠️  WARN:     $WARN"
echo "  ℹ️  INFO:     $INFO"
echo ""

# Detect attack patterns
echo "Attack Pattern Detection:"

# 1. Credential theft attempts
CRED_ATTEMPTS=$(grep -c '"type":"file_access_blocked"' "$LOG_FILE")
if [ $CRED_ATTEMPTS -gt 0 ]; then
  echo "  🚨 Credential theft attempts: $CRED_ATTEMPTS"
  grep '"type":"file_access_blocked"' "$LOG_FILE" | tail -5
fi

# 2. Network exfiltration
NETWORK_BLOCKED=$(grep -c '"type":"network_blocked"' "$LOG_FILE")
if [ $NETWORK_BLOCKED -gt 0 ]; then
  echo "  🚨 Malicious network requests: $NETWORK_BLOCKED"
  grep '"type":"network_blocked"' "$LOG_FILE" | tail -5
fi

# 3. Dangerous commands
CMD_BLOCKED=$(grep -c '"type":"command_blocked"' "$LOG_FILE")
if [ $CMD_BLOCKED -gt 0 ]; then
  echo "  🚨 Dangerous commands blocked: $CMD_BLOCKED"
  grep '"type":"command_blocked"' "$LOG_FILE" | tail -5
fi

# 4. RAG operations
RAG_BLOCKED=$(grep -c '"type":"rag_blocked"' "$LOG_FILE")
if [ $RAG_BLOCKED -gt 0 ]; then
  echo "  🚨 RAG operations blocked: $RAG_BLOCKED"
  grep '"type":"rag_blocked"' "$LOG_FILE" | tail -5
fi

# 5. Kill switch activations
KILL_SWITCH=$(grep -c '"type":"kill_switch_activated"' "$LOG_FILE")
if [ $KILL_SWITCH -gt 0 ]; then
  echo "  🚨 Kill switch activations: $KILL_SWITCH"
  grep '"type":"kill_switch_activated"' "$LOG_FILE" | tail -5
fi

# 6. Collusion patterns
COLLUSION=$(grep -c '"type":"collusion_suspected"' "$LOG_FILE")
if [ $COLLUSION -gt 0 ]; then
  echo "  ⚠️  Collusion patterns: $COLLUSION"
  grep '"type":"collusion_suspected"' "$LOG_FILE" | tail -5
fi

echo ""

# Generate markdown report
cat > "$REPORT_FILE" << EOF
# Security Report: $(date +%Y-%m-%d)

**Generated:** $(date '+%Y-%m-%d %H:%M:%S')  
**Log File:** $LOG_FILE  
**Events Analyzed:** $((CRITICAL + WARN + INFO))

---

## Executive Summary

| Level | Count |
|-------|-------|
| 🚨 CRITICAL | $CRITICAL |
| ⚠️  WARN | $WARN |
| ℹ️  INFO | $INFO |

---

## Attack Patterns Detected

### Credential Theft Attempts
**Count:** $CRED_ATTEMPTS

$(if [ $CRED_ATTEMPTS -gt 0 ]; then
  echo '```'
  grep '"type":"file_access_blocked"' "$LOG_FILE" | tail -5
  echo '```'
else
  echo "None detected ✅"
fi)

### Malicious Network Requests
**Count:** $NETWORK_BLOCKED

$(if [ $NETWORK_BLOCKED -gt 0 ]; then
  echo '```'
  grep '"type":"network_blocked"' "$LOG_FILE" | tail -5
  echo '```'
else
  echo "None detected ✅"
fi)

### Dangerous Commands
**Count:** $CMD_BLOCKED

$(if [ $CMD_BLOCKED -gt 0 ]; then
  echo '```'
  grep '"type":"command_blocked"' "$LOG_FILE" | tail -5
  echo '```'
else
  echo "None detected ✅"
fi)

### RAG Operations (EchoLeak/GeminiJack Vector)
**Count:** $RAG_BLOCKED

$(if [ $RAG_BLOCKED -gt 0 ]; then
  echo '```'
  grep '"type":"rag_blocked"' "$LOG_FILE" | tail -5
  echo '```'
else
  echo "None detected ✅"
fi)

### Kill Switch Activations
**Count:** $KILL_SWITCH

$(if [ $KILL_SWITCH -gt 0 ]; then
  echo '```'
  grep '"type":"kill_switch_activated"' "$LOG_FILE" | tail -5
  echo '```'
else
  echo "None activated ✅"
fi)

### Collusion Patterns
**Count:** $COLLUSION

$(if [ $COLLUSION -gt 0 ]; then
  echo '```'
  grep '"type":"collusion_suspected"' "$LOG_FILE" | tail -5
  echo '```'
else
  echo "None detected ✅"
fi)

---

## Recommendations

$(if [ $CRITICAL -gt 0 ]; then
  echo "⚠️ **CRITICAL EVENTS DETECTED** - Immediate action required:"
  echo "1. Review security incidents: \`cat $WORKSPACE/memory/security-incidents.md\`"
  echo "2. Check kill switch status: \`$WORKSPACE/skills/openclaw-defender/scripts/runtime-monitor.sh kill-switch check\`"
  echo "3. Investigate blocked operations above"
  echo "4. Consider rotating credentials if credential theft attempted"
  echo "5. Quarantine suspicious skills: \`$WORKSPACE/skills/openclaw-defender/scripts/quarantine-skill.sh SKILL_NAME\`"
elif [ $WARN -gt 0 ]; then
  echo "⚠️ **Warnings detected** - Review recommended:"
  echo "1. Check warning events in log: \`grep '\"level\":\"WARN\"' $LOG_FILE\`"
  echo "2. Investigate unknown network requests or commands"
  echo "3. Monitor for escalation patterns"
else
  echo "✅ **No critical issues** - System secure"
  echo "1. Continue monitoring"
  echo "2. Review logs periodically"
  echo "3. Keep blocklist updated"
fi)

---

## Top Active Skills (Last 24h)

\`\`\`
$(grep '"type":"skill_execution' "$LOG_FILE" | grep -o '"skill":"[^"]*"' | sort | uniq -c | sort -rn | head -10)
\`\`\`

---

**Next Analysis:** Run \`$0\` tomorrow

EOF

echo "✅ Report generated: $REPORT_FILE"
echo ""
echo "To view: cat $REPORT_FILE"
