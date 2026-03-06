#!/bin/bash
# Check if news already exists in Notion database (by title or URL)
# Usage: notion-check-duplicate.sh "标题" ["来源URL"]
# Returns: "duplicate" if found, "new" if not found

export https_proxy=http://127.0.0.1:20171
export http_proxy=http://127.0.0.1:20171

NOTION_KEY="${NOTION_KEY:-ntn_YOUR_KEY_HERE}"
DATABASE_ID="${NOTION_DATABASE_ID:-YOUR_DATABASE_ID_HERE}"

TITLE="$1"
SOURCE_URL="$2"

# Build filter: match by title OR by URL
if [ -n "$SOURCE_URL" ]; then
  FILTER=$(cat <<EOF
{
  "filter": {
    "or": [
      {"property": "名称", "title": {"equals": "$TITLE"}},
      {"property": "来源", "url": {"equals": "$SOURCE_URL"}}
    ]
  },
  "page_size": 1
}
EOF
)
else
  FILTER=$(cat <<EOF
{
  "filter": {
    "property": "名称",
    "title": {"equals": "$TITLE"}
  },
  "page_size": 1
}
EOF
)
fi

RESULT=$(curl -s -X POST "https://api.notion.com/v1/databases/$DATABASE_ID/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d "$FILTER")

COUNT=$(echo "$RESULT" | jq -r '.results | length')

if [ "$COUNT" -gt 0 ]; then
  echo "duplicate"
else
  echo "new"
fi
