#!/bin/bash
# GitHunt Search - Find GitHub developers
# Usage: githunt-search.sh <location> [skills] [limit]
#
# Examples:
#   githunt-search.sh berlin "react,typescript" 10
#   githunt-search.sh "san francisco" python
#   githunt-search.sh germany "go,kubernetes" 50

API_URL="${GITHUNT_API_URL:-https://api.githunt.ai/v1}"

location="${1:-}"
skills="${2:-}"
limit="${3:-20}"

if [ -z "$location" ]; then
  echo "Usage: githunt-search.sh <location> [skills] [limit]"
  echo ""
  echo "Examples:"
  echo "  githunt-search.sh berlin 'react,typescript' 10"
  echo "  githunt-search.sh 'san francisco' python"
  echo "  githunt-search.sh germany 'go,kubernetes' 50"
  exit 1
fi

# Build skills array for JSON
if [ -n "$skills" ]; then
  skills_json=$(echo "$skills" | sed 's/,/","/g' | sed 's/^/["/' | sed 's/$/"]/')
else
  skills_json="[]"
fi

# Build JSON payload
payload=$(cat <<EOF
{
  "location": "$location",
  "skills": $skills_json,
  "maxUsers": $limit
}
EOF
)

echo "🔍 Searching for developers in '$location'..."
[ -n "$skills" ] && echo "   Skills: $skills"
echo ""

# Make request
response=$(curl -s -X POST "$API_URL/rank/users" \
  -H "Content-Type: application/json" \
  -H "Accept-Encoding: gzip" \
  -d "$payload" --compressed 2>/dev/null)

# Check if response is valid JSON
if ! echo "$response" | jq . >/dev/null 2>&1; then
  echo "❌ API error or invalid response"
  echo "$response"
  exit 1
fi

# Pretty print results
echo "$response" | jq -r '
  "Found \(.totalCount // .results | length) developers:\n",
  (.results[:20] | .[] | 
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "👤 \(.name // .login) (@\(.login))",
    "📍 \(.location // "Unknown")",
    "⭐ Score: \(.score // "N/A")/100",
    "🏢 \(.company // "—")",
    "📧 \(.email // "—")",
    "💼 Hireable: \(if .isHireable then "Yes ✓" else "—" end)",
    "🔧 \((.technologies // .languages // [])[:5] | join(", "))",
    "🔗 https://github.com/\(.login)",
    ""
  )
'
