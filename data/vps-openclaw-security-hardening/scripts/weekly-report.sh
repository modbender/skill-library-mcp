#!/bin/bash
# Weekly Security Report - Comprehensive weekly summary
# Called by cron weekly

REPORT_FILE="/tmp/weekly-security-report.txt"
ALERT_CONFIG="$(dirname "$0")/../config/alerting.env"

echo "Weekly Security Report - $(date '+%Y-%m-%d')" > "$REPORT_FILE"
echo "==============================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Summary of week's events
echo "Security Events This Week:" >> "$REPORT_FILE"
echo "-------------------------" >> "$REPORT_FILE"
ausearch -ts this-week -k agent_ -i 2>/dev/null | tail -50 >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "Failed SSH Attempts:" >> "$REPORT_FILE"
echo "-------------------" >> "$REPORT_FILE"
grep "Failed password" /var/log/auth.log 2>/dev/null | tail -20 >> "$REPORT_FILE" || echo "No failed attempts logged" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "UFW Status:" >> "$REPORT_FILE"
echo "----------" >> "$REPORT_FILE"
sudo ufw status numbered 2>/dev/null >> "$REPORT_FILE" || echo "UFW not active" >> "$REPORT_FILE"

# Send report if configured
if [ -f "$ALERT_CONFIG" ]; then
    source "$ALERT_CONFIG"
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d chat_id="${TELEGRAM_CHAT_ID}" \
            -d text="$(cat $REPORT_FILE | head -100)" \
            -d parse_mode="HTML" 2>/dev/null
    fi
fi

rm -f "$REPORT_FILE"
exit 0
