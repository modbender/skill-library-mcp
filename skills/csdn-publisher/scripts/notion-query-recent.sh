#!/bin/bash
# Query recent news from Notion database
# Usage: notion-query-recent.sh [days] 
# Default: last 7 days. Output: title | url | date (one per line)

export https_proxy=http://127.0.0.1:20171
export http_proxy=http://127.0.0.1:20171

NOTION_KEY="${NOTION_KEY:-ntn_YOUR_KEY_HERE}"
DATABASE_ID="${NOTION_DATABASE_ID:-YOUR_DATABASE_ID_HERE}"

DAYS="${1:-7}"
SINCE=$(date -d "-${DAYS} days" +%Y-%m-%d 2>/dev/null || date -v-${DAYS}d +%Y-%m-%d)

FILTER=$(cat <<EOF
{
  "filter": {
    "property": "日期",
    "date": {"on_or_after": "$SINCE"}
  },
  "page_size": 100,
  "sorts": [{"property": "日期", "direction": "descending"}]
}
EOF
)

curl -s -X POST "https://api.notion.com/v1/databases/$DATABASE_ID/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d "$FILTER" | jq -r '.results[] | "\(.properties["名称"].title[0].text.content) | \(.properties["来源"].url // "无") | \(.properties["日期"].date.start)"'
