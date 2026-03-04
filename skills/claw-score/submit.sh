#!/bin/bash
# Claw Score Submission Script
# Packages workspace files, sanitizes, and submits for audit

set -e

WEBHOOK_URL="https://atlasforge.me/api/claw-score/submit"
WORKSPACE="${1:-.}"
EMAIL="${2:-}"

if [ -z "$EMAIL" ]; then
    echo "Usage: ./submit.sh [workspace_path] <email>"
    echo "Example: ./submit.sh . you@example.com"
    exit 1
fi

echo "🦀 Claw Score Audit Submission"
echo "=============================="
echo ""

# Files to collect
FILES=(
    "AGENTS.md"
    "SOUL.md"
    "MEMORY.md"
    "TOOLS.md"
    "SECURITY.md"
    "HEARTBEAT.md"
    "USER.md"
    "IDENTITY.md"
)

# Build JSON payload
PAYLOAD='{"email":"'"$EMAIL"'","files":{},"file_tree":[]}'

# Collect files
for file in "${FILES[@]}"; do
    if [ -f "$WORKSPACE/$file" ]; then
        echo "✓ Found: $file"
        # Read file, sanitize, escape for JSON
        CONTENT=$(cat "$WORKSPACE/$file" | \
            sed -E 's/[a-zA-Z0-9_-]*[Kk][Ee][Yy][a-zA-Z0-9_-]*[=:][[:space:]]*[^[:space:]\n]+/[REDACTED]/g' | \
            sed -E 's/sk-[a-zA-Z0-9]+/[API_KEY_REDACTED]/g' | \
            sed -E 's/xoxb-[a-zA-Z0-9-]+/[TOKEN_REDACTED]/g' | \
            sed -E 's/ghp_[a-zA-Z0-9]+/[TOKEN_REDACTED]/g' | \
            sed -E 's/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/[EMAIL_REDACTED]/g' | \
            sed -E 's/\+?[0-9]{1,3}[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}/[PHONE_REDACTED]/g' | \
            sed -E 's/([0-9]{1,3}\.){3}[0-9]{1,3}/[IP_REDACTED]/g' | \
            python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
        
        PAYLOAD=$(echo "$PAYLOAD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
data['files']['$file'] = $CONTENT
print(json.dumps(data))
")
    else
        echo "- Not found: $file"
    fi
done

# Get file tree (top level only, no contents)
echo ""
echo "Collecting file tree..."
TREE=$(find "$WORKSPACE" -maxdepth 2 -type d -name ".*" -prune -o -type f -name "*.md" -print -o -type d -print 2>/dev/null | head -50 | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin]))")
PAYLOAD=$(echo "$PAYLOAD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
data['file_tree'] = $TREE
print(json.dumps(data))
")

echo ""
echo "=============================="
echo "Ready to submit to Atlas for Claw Score audit."
echo "Email: $EMAIL"
echo ""
read -p "Proceed? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Submitting..."
    RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")
    
    if echo "$RESPONSE" | grep -q '"success":true'; then
        echo ""
        echo "✅ Submission successful!"
        echo "You'll receive your Claw Score report at $EMAIL within 24-48 hours."
    else
        echo ""
        echo "❌ Submission failed. Response:"
        echo "$RESPONSE"
        echo ""
        echo "You can manually email your files to: atlasai@fastmail.com"
    fi
else
    echo "Submission cancelled."
fi
