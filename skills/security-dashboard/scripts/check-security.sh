#!/bin/bash
# Check Security Dashboard for critical issues and report

API_URL="http://localhost:18791/api/security"
ALERT_THRESHOLD="critical"  # Report critical alerts immediately

# Fetch security metrics
RESPONSE=$(curl -s "$API_URL")

if [ -z "$RESPONSE" ]; then
    echo "⚠️ Security Dashboard API not responding"
    exit 1
fi

# Parse overall status
STATUS_LEVEL=$(echo "$RESPONSE" | jq -r '.status.level')
STATUS_TEXT=$(echo "$RESPONSE" | jq -r '.status.text')

# Check critical security components directly
FIREWALL_STATUS=$(echo "$RESPONSE" | jq -r '.network.firewall')
FAIL2BAN_STATUS=$(echo "$RESPONSE" | jq -r '.ssh.fail2ban')

# Get critical alerts from dashboard
CRITICAL_ALERTS=$(echo "$RESPONSE" | jq -r '.alerts[] | select(.level == "critical") | "\(.title): \(.message)"')
CRITICAL_COUNT=$(echo "$RESPONSE" | jq '[.alerts[] | select(.level == "critical")] | length')

# Elevate firewall and fail2ban to critical if inactive
CRITICAL_ISSUES=()

if [ "$FIREWALL_STATUS" = "Inactive" ]; then
    CRITICAL_ISSUES+=("Firewall Inactive: Network protection disabled. Enable UFW or firewalld immediately.")
    ((CRITICAL_COUNT++))
fi

if [ "$FAIL2BAN_STATUS" = "Inactive" ] || [ "$FAIL2BAN_STATUS" = "inactive" ]; then
    CRITICAL_ISSUES+=("fail2ban Inactive: SSH brute-force protection disabled. Enable fail2ban service.")
    ((CRITICAL_COUNT++))
fi

# Combine dashboard critical alerts with our elevated checks
if [ -n "$CRITICAL_ALERTS" ]; then
    while IFS= read -r alert; do
        CRITICAL_ISSUES+=("$alert")
    done <<< "$CRITICAL_ALERTS"
fi

# Get warning alerts
WARNING_ALERTS=$(echo "$RESPONSE" | jq -r '.alerts[] | select(.level == "warning") | "\(.title): \(.message)"')
WARNING_COUNT=$(echo "$RESPONSE" | jq '[.alerts[] | select(.level == "warning")] | length')

# Build report if issues found
if [ "$STATUS_LEVEL" = "critical" ] || [ "$CRITICAL_COUNT" -gt 0 ]; then
    REPORT="🚨 **CRITICAL SECURITY ISSUES DETECTED**\n\n"
    REPORT+="Status: $STATUS_TEXT\n"
    REPORT+="Critical Alerts: $CRITICAL_COUNT\n"
    
    if [ "$CRITICAL_COUNT" -gt 0 ]; then
        REPORT+="\n**Critical Issues:**\n"
        for issue in "${CRITICAL_ISSUES[@]}"; do
            REPORT+="- $issue\n"
        done
    fi
    
    if [ "$WARNING_COUNT" -gt 0 ]; then
        REPORT+="\n**Warnings ($WARNING_COUNT):**\n"
        while IFS= read -r alert; do
            REPORT+="- $alert\n"
        done <<< "$WARNING_ALERTS"
    fi
    
    REPORT+="\nDashboard: http://localhost:18791 (via SSH port forwarding)"
    
    # Output report (will be captured by cron and sent as system event)
    echo -e "$REPORT"
    exit 1
    
elif [ "$WARNING_COUNT" -gt 0 ]; then
    # Only report warnings if significant (3+ warnings)
    if [ "$WARNING_COUNT" -ge 3 ]; then
        REPORT="⚠️ **Security Warnings Detected**\n\n"
        REPORT+="Status: $STATUS_TEXT\n"
        REPORT+="Warning Count: $WARNING_COUNT\n\n"
        
        REPORT+="**Issues:**\n"
        while IFS= read -r alert; do
            REPORT+="- $alert\n"
        done <<< "$WARNING_ALERTS"
        
        REPORT+="\nDashboard: http://localhost:18791 (via SSH port forwarding)"
        
        echo -e "$REPORT"
        exit 1
    fi
fi

# All clear - no output (silent success)
exit 0
