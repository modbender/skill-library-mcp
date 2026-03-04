#!/bin/bash
# KB Collector - Digest Generator
# Usage: ./digest.sh [weekly|monthly|yearly] [--send]

TYPE="${1:-weekly}"
VAULT="/Users/george/Documents/Georges/Knowledge"
RECIPIENT="george@precaster.com.tw"
EMAIL="george@precaster.com.tw"
APP_PASSWORD="yxio cqru vchu jgdo"

# Date ranges
case "$TYPE" in
    weekly)
        SINCE=$(date -v-7d +%Y-%m-%d 2>/dev/null || date -d "7 days ago" +%Y-%m-%d)
        SUBJECT="📊 每週知識摘要 $(date +%Y-%m-%d)"
        ;;
    monthly)
        SINCE=$(date -v-30d +%Y-%m-%d 2>/dev/null || date -d "30 days ago" +%Y-%m-%d)
        SUBJECT="📊 每月知識摘要 $(date +%Y-%m)"
        ;;
    yearly)
        SINCE="2025-01-01"
        SUBJECT="🎯 年度回顧與展望 $(date +%Y)"
        ;;
    *)
        echo "Usage: digest.sh [weekly|monthly|yearly] [--send]"
        exit 1
        ;;
esac

# Check for --send flag
SEND_EMAIL=""
if [[ "$2" == "--send" ]]; then
    SEND_EMAIL="yes"
fi

echo "Generating $TYPE digest since $SINCE..."

# Extract tags and titles from markdown files
> /tmp/digest_tags.txt

for file in "$VAULT"/*.md; do
    [ -f "$file" ] || continue
    
    CREATED=$(grep -m1 "^created:" "$file" 2>/dev/null | sed 's/created: *//' | cut -d'T' -f1)
    # Also check for date: field as fallback
    if [ -z "$CREATED" ]; then
        CREATED=$(grep -m1 "^date:" "$file" 2>/dev/null | sed 's/date: *//' | cut -d'T' -f1)
    fi
    [ -z "$CREATED" ] && continue
    
    if [[ "$CREATED" < "$SINCE" ]]; then
        continue
    fi
    
    TITLE=$(grep -m1 "^# " "$file" 2>/dev/null | sed 's/^# //')
    [ -z "$TITLE" ] && TITLE="${file##*/}"
    
    TAGS=$(grep -m1 "^tags:" "$file" 2>/dev/null | sed 's/.*tags: *\[//' | sed 's/\]//' | tr ',' '\n' | tr -d ' ' | grep -v '^$')
    
    if [ -n "$TAGS" ]; then
        for tag in $TAGS; do
            echo "$tag|$TITLE|${file##*/}"
        done
    else
        echo "無標籤|$TITLE|${file##*/}"
    fi
done | sort >> /tmp/digest_tags.txt

# Generate report
case "$TYPE" in
    weekly|monthly)
        echo "=== $TYPE Digest ===" > /tmp/digest_content.txt
        echo "" >> /tmp/digest_content.txt
        echo "## 📈 標籤統計" >> /tmp/digest_content.txt
        echo "" >> /tmp/digest_content.txt
        cut -d'|' -f1 /tmp/digest_tags.txt | sort | uniq -c | sort -rn | head -10 | while read count tag; do
            echo "- **$tag**: $count 篇" >> /tmp/digest_content.txt
        done
        echo "" >> /tmp/digest_content.txt
        echo "## 📝 近期筆記" >> /tmp/digest_content.txt
        echo "" >> /tmp/digest_content.txt
        cut -d'|' -f2 /tmp/digest_tags.txt | head -20 | while read title; do
            echo "- $title" >> /tmp/digest_content.txt
        done
        ;;
    yearly)
        echo "=== 年度回顧 ===" > /tmp/digest_content.txt
        echo "" >> /tmp/digest_content.txt
        echo "## 🔥 熱門標籤" >> /tmp/digest_content.txt
        echo "" >> /tmp/digest_content.txt
        cut -d'|' -f1 /tmp/digest_tags.txt | sort | uniq -c | sort -rn | head -15 | while read count tag; do
            echo "- **$tag**: $count 篇" >> /tmp/digest_content.txt
        done
        echo "" >> /tmp/digest_content.txt
        echo "## 💡 發展建議" >> /tmp/digest_content.txt
        echo "" >> /tmp/digest_content.txt
        echo "根據今年的知識收集趨勢：" >> /tmp/digest_content.txt
        echo "" >> /tmp/digest_content.txt
        echo "1. 持續關注核心領域" >> /tmp/digest_content.txt
        echo "2. 探索新興技術趨勢" >> /tmp/digest_content.txt
        echo "3. 建立更多跨領域連結" >> /tmp/digest_content.txt
        ;;
esac

# Display
echo ""
cat /tmp/digest_content.txt

# Send email if requested
if [ -n "$SEND_EMAIL" ]; then
    echo ""
    echo "Sending email to $RECIPIENT..."
    python3 - << EOF
import smtplib
from email.mime.text import MIMEText

with open('/tmp/digest_content.txt', 'r') as f:
    body = f.read()

msg = MIMEText(body, 'plain', 'utf-8')
msg['Subject'] = '$SUBJECT'
msg['From'] = '$EMAIL'
msg['To'] = '$RECIPIENT'

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('$EMAIL', '$APP_PASSWORD')
server.send_message(msg)
server.quit()
print('Email sent!')
EOF
fi

rm -f /tmp/digest_tags.txt /tmp/digest_content.txt
echo ""
echo "Done!"
