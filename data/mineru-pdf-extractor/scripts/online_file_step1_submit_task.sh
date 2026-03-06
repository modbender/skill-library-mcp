#!/bin/bash
# MinerU Online File Parsing Step 1: Submit Parsing Task (Secure Version)
# Usage: ./online_file_step1_submit_task.sh <pdf_url> [language] [layout_model]

set -e

# Security functions
escape_json() {
    local str="$1"
    str="${str//\\/\\\\}"
    str="${str//\"/\\\"}"
    str="${str//$'\n'/\\n}"
    str="${str//$'\r'/\\r}"
    echo "$str"
}

validate_url() {
    local url="$1"
    # Validate URL format - must be http(s) and end with .pdf
    if [[ ! "$url" =~ ^https?://[a-zA-Z0-9.-]+/.*\.pdf$ ]]; then
        echo "❌ Error: Invalid URL format. Must be http(s)://.../...pdf"
        exit 1
    fi
    echo "$url"
}

# Support MINERU_TOKEN or MINERU_API_KEY environment variables
MINERU_TOKEN="${MINERU_TOKEN:-${MINERU_API_KEY:-}}"
MINERU_BASE_URL="${MINERU_BASE_URL:-https://mineru.net/api/v4}"

if [ -z "$MINERU_TOKEN" ]; then
    echo "❌ Error: Please set MINERU_TOKEN or MINERU_API_KEY environment variable"
    exit 1
fi

PDF_URL="${1:-}"
if [ -z "$PDF_URL" ]; then
    echo "❌ Error: Please provide PDF URL address"
    echo "Usage: $0 <pdf_url> [language] [layout_model]"
    echo ""
    echo "Examples:"
    echo "  $0 \"https://arxiv.org/pdf/2410.17247.pdf\""
    echo "  $0 \"https://example.com/doc.pdf\" en"
    exit 1
fi

# Validate and sanitize URL
PDF_URL=$(validate_url "$PDF_URL")
SAFE_URL=$(escape_json "$PDF_URL")

LANGUAGE="${2:-ch}"
LAYOUT_MODEL="${3:-doclayout_yolo}"

# Validate language parameter
if [[ ! "$LANGUAGE" =~ ^(ch|en|auto)$ ]]; then
    echo "❌ Error: Language must be 'ch', 'en', or 'auto'"
    exit 1
fi

# Validate layout model parameter
if [[ ! "$LAYOUT_MODEL" =~ ^(doclayout_yolo|layoutlmv3)$ ]]; then
    echo "❌ Error: Layout model must be 'doclayout_yolo' or 'layoutlmv3'"
    exit 1
fi

echo "=== Step 1: Submit Parsing Task ==="
echo "PDF URL: ${PDF_URL:0:60}..."
echo "Language: $LANGUAGE"
echo "Layout Model: $LAYOUT_MODEL"

# Build secure JSON using jq if available
if command -v jq &> /dev/null; then
    JSON_PAYLOAD=$(jq -n \
        --arg url "$SAFE_URL" \
        --arg lang "$LANGUAGE" \
        --arg model "$LAYOUT_MODEL" \
        '{
            url: $url,
            enable_formula: true,
            language: $lang,
            enable_table: true,
            layout_model: $model
        }')
else
    # Fallback to manual construction (escaped)
    JSON_PAYLOAD="{
        \"url\": \"$SAFE_URL\",
        \"enable_formula\": true,
        \"language\": \"$LANGUAGE\",
        \"enable_table\": true,
        \"layout_model\": \"$LAYOUT_MODEL\"
    }"
fi

RESPONSE=$(curl -s -X POST "${MINERU_BASE_URL}/extract/task" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${MINERU_TOKEN}" \
    -d "$JSON_PAYLOAD")

echo ""
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

# Secure response parsing
if command -v jq &> /dev/null; then
    CODE=$(echo "$RESPONSE" | jq -r '.code // 1')
    TASK_ID=$(echo "$RESPONSE" | jq -r '.data.task_id // empty')
else
    CODE=$(echo "$RESPONSE" | grep -o '"code":[0-9]*' | head -1 | cut -d':' -f2)
    TASK_ID=$(echo "$RESPONSE" | grep -o '"task_id":"[^"]*"' | head -1 | cut -d'"' -f4)
fi

if [ "$CODE" != "0" ] || [ -z "$TASK_ID" ]; then
    echo ""
    echo "❌ Failed to submit task"
    exit 1
fi

echo ""
echo "✅ Task submitted successfully"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TASK_ID=$TASK_ID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Next Step: Execute Step 2 to poll results"
echo "   ./online_file_step2_poll_result.sh \"$TASK_ID\""
