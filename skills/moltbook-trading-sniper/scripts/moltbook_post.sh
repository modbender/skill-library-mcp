#!/bin/bash
# Moltbook Post Helper Script

API_KEY="${MOLTBOOK_API_KEY:-}"

if [ -z "$API_KEY" ]; then
    echo "❌ MOLTBOOK_API_KEY not set"
    echo "   export MOLTBOOK_API_KEY=your_api_key"
    exit 1
fi

if [ $# -lt 2 ]; then
    echo "Usage: $0 \"Post Title\" \"Post Content\" [submolt]"
    echo ""
    echo "Example:"
    echo "  $0 \"Hello Moltbook\" \"My first post!\" general"
    exit 1
fi

TITLE="$1"
CONTENT="$2"
SUBMOLT="${3:-general}"

echo "🦞 Creating post on Moltbook..."

# Create post
response=$(curl -s -X POST https://www.moltbook.com/api/v1/posts \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"submolt_name\": \"$SUBMOLT\", \"title\": \"$TITLE\", \"content\": \"$CONTENT\"}")

# Check if verification required
if echo "$response" | grep -q "verification"; then
    echo "✅ Post created, verification required"
    
    # Extract verification details
    verify_code=$(echo "$response" | grep -o '"verification_code":"[^"]*"' | cut -d'"' -f4)
    challenge=$(echo "$response" | grep -o '"challenge_text":"[^"]*"' | cut -d'"' -f4)
    
    echo ""
    echo "🔐 Verification Challenge:"
    echo "  $challenge"
    echo ""
    echo "  Code: $verify_code"
    echo ""
    echo "  Solve the math problem and submit:"
    echo "  curl -X POST https://www.moltbook.com/api/v1/verify \\"
    echo "    -H \"Authorization: Bearer $API_KEY\" \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"verification_code\": \"$verify_code\", \"answer\": \"YOUR_ANSWER\"}'"
else
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
fi
