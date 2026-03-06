#!/bin/bash
# MinerU Local File Parsing Step 1: Apply for Upload URL (Secure Version)
# Usage: ./local_file_step1_apply_upload_url.sh <pdf_file_path> [language] [layout_model]

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

validate_filename() {
    local filename="$1"
    # Only allow alphanumeric, dots, underscores, hyphens
    if [[ ! "$filename" =~ ^[a-zA-Z0-9._-]+$ ]]; then
        echo "⚠️  Warning: Filename contains special characters, sanitizing..."
        filename=$(echo "$filename" | tr -cd 'a-zA-Z0-9._-')
    fi
    echo "$filename"
}

# Support MINERU_TOKEN or MINERU_API_KEY environment variables
MINERU_TOKEN="${MINERU_TOKEN:-${MINERU_API_KEY:-}}"
MINERU_BASE_URL="${MINERU_BASE_URL:-https://mineru.net/api/v4}"

if [ -z "$MINERU_TOKEN" ]; then
    echo "❌ Error: Please set MINERU_TOKEN or MINERU_API_KEY environment variable"
    exit 1
fi

PDF_PATH="${1:-}"
if [ -z "$PDF_PATH" ] || [ ! -f "$PDF_PATH" ]; then
    echo "❌ Error: Please provide a valid PDF file path"
    echo "Usage: $0 <pdf_file_path> [language] [layout_model]"
    exit 1
fi

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

FILENAME=$(basename "$PDF_PATH")
# Sanitize filename
FILENAME=$(validate_filename "$FILENAME")
SAFE_FILENAME=$(escape_json "$FILENAME")

echo "=== Step 1: Apply for Upload URL ==="
echo "File: $FILENAME"
echo "Language: $LANGUAGE"
echo "Layout Model: $LAYOUT_MODEL"

# Build secure JSON using jq if available
if command -v jq &> /dev/null; then
    JSON_PAYLOAD=$(jq -n \
        --arg name "$SAFE_FILENAME" \
        --arg lang "$LANGUAGE" \
        --arg model "$LAYOUT_MODEL" \
        '{
            enable_formula: true,
            language: $lang,
            enable_table: true,
            layout_model: $model,
            enable_ocr: true,
            files: [{name: $name, is_ocr: true}]
        }')
else
    # Fallback to manual construction (escaped)
    JSON_PAYLOAD="{
        \"enable_formula\": true,
        \"language\": \"$LANGUAGE\",
        \"enable_table\": true,
        \"layout_model\": \"$LAYOUT_MODEL\",
        \"enable_ocr\": true,
        \"files\": [{\"name\": \"$SAFE_FILENAME\", \"is_ocr\": true}]
    }"
fi

RESPONSE=$(curl -s -X POST "${MINERU_BASE_URL}/file-urls/batch" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${MINERU_TOKEN}" \
    -d "$JSON_PAYLOAD")

echo ""
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

# Secure response parsing
if command -v jq &> /dev/null; then
    CODE=$(echo "$RESPONSE" | jq -r '.code // 1')
    BATCH_ID=$(echo "$RESPONSE" | jq -r '.data.batch_id // empty')
    UPLOAD_URL=$(echo "$RESPONSE" | jq -r '.data.file_urls[0] // empty')
else
    CODE=$(echo "$RESPONSE" | grep -o '"code":[0-9]*' | head -1 | cut -d':' -f2)
    BATCH_ID=$(echo "$RESPONSE" | grep -o '"batch_id":"[^"]*"' | head -1 | cut -d'"' -f4)
    UPLOAD_URL=$(echo "$RESPONSE" | grep -o '"file_urls":\[[^\]]*\]' | grep -o '"https://[^"]*"' | head -1 | tr -d '"')
fi

if [ "$CODE" != "0" ] || [ -z "$BATCH_ID" ]; then
    echo ""
    echo "❌ Failed to apply for upload URL"
    exit 1
fi

echo ""
echo "✅ Success"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "BATCH_ID=$BATCH_ID"
echo "UPLOAD_URL=$UPLOAD_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Next Step: Execute Step 2 to upload file"
echo "   ./local_file_step2_upload_file.sh \"$UPLOAD_URL\" \"$PDF_PATH\""
