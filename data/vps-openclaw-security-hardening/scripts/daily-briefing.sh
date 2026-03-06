#!/bin/bash
# Daily Security Briefing for OpenClaw
# Run via cron: 0 8 * * * root /path/to/daily-briefing.sh

set -euo pipefail

CONFIG_FILE="$(dirname "$0")/../config/alerting.env"
[[ -f "$CONFIG_FILE" ]] && source "$CONFIG_FILE"

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

# Risk scoring weights
declare -A RISK_WEIGHTS=(
    ["credential_access"]=100
    ["ssh_config_change"]=90
    ["privilege_escalation"]=95
    ["failed_login"]=30
    ["permission_change"]=20
    ["firewall_change"]=80
    ["audit_tamper"]=100
    ["normal_activity"]=5
)

generate_report() {
    local date
    date=$(date '+%Y-%m-%d')
    
    # Collect metrics
    local cred_access
    cred_access=$(ausearch -ts today -k agent_credentials 2>/dev/null | grep -c 'type=PATH' || echo 0)
    
    local ssh_changes
    ssh_changes=$(ausearch -ts today -k agent_ssh_config 2>/dev/null | grep -c 'type=PATH' || echo 0)
    
    local failed_logins
    failed_logins=$(grep "Failed password" /var/log/auth.log 2>/dev/null | wc -l || echo 0)
    
    local successful_logins
    successful_logins=$(grep "Accepted publickey" /var/log/auth.log 2>/dev/null | wc -l || echo 0)
    
    local priv_esc
    priv_esc=$(ausearch -ts today -k agent_privesc 2>/dev/null | grep -c 'type=SYSCALL' || echo 0)
    
    local file_changes
    file_changes=$(ausearch -ts today -k agent_home 2>/dev/null | grep -c 'type=PATH' || echo 0)
    
    # Calculate risk score
    local risk_score=0
    ((risk_score += cred_access * RISK_WEIGHTS["credential_access"]))
    ((risk_score += ssh_changes * RISK_WEIGHTS["ssh_config_change"]))
    ((risk_score += failed_logins * RISK_WEIGHTS["failed_login"]))
    ((risk_score += priv_esc * RISK_WEIGHTS["privilege_escalation"]))
    
    # Normalize to 0-100 scale
    risk_score=$((risk_score > 100 ? 100 : risk_score))
    
    # Determine risk level
    local risk_level="🟢 LOW"
    [[ $risk_score -ge 30 ]] && risk_level="🟡 MEDIUM"
    [[ $risk_score -ge 60 ]] && risk_level="🟠 HIGH"
    [[ $risk_score -ge 80 ]] && risk_level="🔴 CRITICAL"
    
    # Generate briefing
    cat <> EOF
📊 *DAILY SECURITY BRIEFING*
*Date:* ${date}
*Status:* ${risk_level}

━━━━━━━━━━━━━━━━━━━━━━━
🛡️ *SECURITY SUMMARY*
━━━━━━━━━━━━━━━━━━━━━━━
🔐 Credential Access: ${cred_access}
📝 SSH Config Changes: ${ssh_changes}
🔑 SSH Keys Accessed: $(ausearch -ts today -k agent_ssh_keys 2>/dev/null | grep -c 'type=PATH' || echo 0)
🚪 Successful Logins: ${successful_logins}
🚫 Failed Logins: ${failed_logins}
🧱 Firewall Changes: $(ausearch -ts today -k agent_firewall 2>/dev/null | grep -c 'type=PATH' || echo 0)

━━━━━━━━━━━━━━━━━━━━━━━
⚡ *ACTIVITY SUMMARY*
━━━━━━━━━━━━━━━━━━━━━━━
🤖 Agent Directory Changes: ${file_changes}
⚠️ Privilege Escalation Attempts: ${priv_esc}
📁 Security Repo Changes: $(ausearch -ts today -k agent_security_repo 2>/dev/null | grep -c 'type=PATH' || echo 0)

━━━━━━━━━━━━━━━━━━━━━━━
📈 *RISK ASSESSMENT*
━━━━━━━━━━━━━━━━━━━━━━━
Score: ${risk_score}/100
Level: ${risk_level}

━━━━━━━━━━━━━━━━━━━━━━━
✅ *RECOMMENDED ACTIONS*
━━━━━━━━━━━━━━━━━━━━━━━
EOF
    
    # Add recommendations based on findings
    if [[ $cred_access -gt 0 ]]; then
        echo "⚠️ Review credential access: \`ausearch -ts today -k agent_credentials\`"
    fi
    
    if [[ $ssh_changes -gt 0 ]]; then
        echo "⚠️ Verify SSH changes: \`ausearch -ts today -k agent_ssh_config\`"
    fi
    
    if [[ $failed_logins -gt 5 ]]; then
        echo "⚠️ Multiple failed logins detected - check for brute force"
    fi
    
    if [[ $risk_score -lt 20 ]]; then
        echo "✓ All systems nominal. No action required."
    fi
    
    echo ""
    echo "_Next briefing: Tomorrow 08:00 CET_"
}

send_briefing() {
    local report
    report=$(generate_report)
    
    if [[ -z "$TELEGRAM_BOT_TOKEN" || -z "$TELEGRAM_CHAT_ID" ]]; then
        echo "$report" > /var/log/agent-daily-briefing.log
        echo "Briefing logged to /var/log/agent-daily-briefing.log (Telegram not configured)"
        return 0
    fi
    
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "parse_mode=Markdown" \
        -d "text=${report}" \
        --max-time 30 \
        > /dev/null 2>&1 || {
        echo "$report" > /var/log/agent-daily-briefing.log
        echo "Failed to send Telegram, logged locally"
        return 1
    }
    
    echo "Briefing sent successfully"
}

# Main
main() {
    # Save to local log regardless
    generate_report > /var/log/agent-daily-briefing.log
    
    # Send via Telegram if configured
    if [[ -n "$TELEGRAM_BOT_TOKEN" && -n "$TELEGRAM_CHAT_ID" ]]; then
        send_briefing
    else
        cat /var/log/agent-daily-briefing.log
        echo ""
        echo "To enable Telegram delivery, configure $CONFIG_FILE"
    fi
}

main "$@"
