#!/usr/bin/env bash
# Email Processor Script - Processes unread emails and categorizes them

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📧 Email Processor"
echo "=================="

# Check dependencies
if ! command -v gog &> /dev/null; then
    echo -e "${RED}Error: gog CLI not found${NC}"
    echo "Install: brew install steipete/tap/gogcli"
    exit 1
fi

# Check authentication
if ! gog auth list &> /dev/null; then
    echo -e "${RED}Error: gog not authenticated${NC}"
    echo "Run: gog auth credentials /path/to/client_secret.json"
    echo "Then: gog auth add your@email.com --services gmail"
    exit 1
fi

# Get unread count
echo "Fetching unread emails..."
UNREAD_JSON=$(gog gmail search 'is:unread' --json --max 200 2>/dev/null) || {
    echo -e "${RED}Error: Failed to fetch emails. Check gog authentication.${NC}"
    exit 1
}

TOTAL_COUNT=$(echo "$UNREAD_JSON" | jq '.threads | length')
echo "Found $TOTAL_COUNT unread emails"

if [ "$TOTAL_COUNT" -eq 0 ]; then
    echo -e "${GREEN}No unread emails!${NC}"
    exit 0
fi

# Extract and categorize
MARKETING_IDS=$(echo "$UNREAD_JSON" | jq -r '.threads[] | select(.labels | contains(["[Superhuman]/AI/News"]) or contains(["[Superhuman]/AI/Marketing"]) or contains(["[Superhuman]/AI/AutoArchived"]) or contains(["CATEGORY_PROMOTIONS"])) | .id')
NEWSLETTER_IDS=$(echo "$UNREAD_JSON" | jq -r '.threads[] | select(.labels | contains(["[Superhuman]/AI/Pitch"])) | .id')

MARKETING_COUNT=$(echo "$MARKETING_IDS" | grep -c '^' || true)
NEWSLETTER_COUNT=$(echo "$NEWSLETTER_IDS" | grep -c '^' || true)

# Mark marketing as read
echo ""
echo "Processing marketing/news emails..."
MARKED=0
for id in $MARKETING_IDS; do
    if gog gmail thread modify "$id" --remove UNREAD --force &>/dev/null; then
        ((MARKED++))
        echo -n "."
    fi
done

for id in $NEWSLETTER_IDS; do
    if gog gmail thread modify "$id" --remove UNREAD --force &>/dev/null; then
        ((MARKED++))
        echo -n "."
    fi
done

echo ""
echo -e "${GREEN}Marked $MARKED emails as read${NC}"

# Generate important emails report
IMPORTANT=$(echo "$UNREAD_JSON" | jq -r '.threads[] | select(.labels | contains(["IMPORTANT"]) or contains(["CATEGORY_UPDATES"])) | select(.labels | contains(["[Superhuman]/AI/News"]) or contains(["[Superhuman]/AI/Marketing"]) or contains(["[Superhuman]/AI/Pitch"]) or contains(["[Superhuman]/AI/AutoArchived"]) or contains(["CATEGORY_PROMOTIONS"]) | not) | {id: .id, from: .from, subject: .subject, date: .date}')

if [ -n "$IMPORTANT" ]; then
    echo ""
    echo "📋 Emails Requiring Attention:"
    echo "=============================="
    echo "$UNREAD_JSON" | jq -r '.threads[] | select(.labels | contains(["IMPORTANT"])) | "[IMPORTANT] \(.from) - \(.subject) [\(.date)]"'
    echo "$UNREAD_JSON" | jq -r '.threads[] | select(.labels | contains(["CATEGORY_UPDATES"])) | select(.labels | contains(["[Superhuman]/AI/News","[Superhuman]/AI/Marketing","[Superhuman]/AI/Pitch","[Superhuman]/AI/AutoArchived","CATEGORY_PROMOTIONS"]) | not) | "[UPDATE] \(.from) - \(.subject) [\(.date)]"' | head -20
fi

# Generate summary
echo ""
echo "=================="
echo "Summary:"
echo "  Total unread: $TOTAL_COUNT"
echo "  Marked as read: $MARKED"
echo "  Remaining: $((TOTAL_COUNT - MARKED))"
echo "=================="
