#!/bin/bash
# MinerU Online File Parsing Step 2: Poll Extraction Results and Download (Secure Version)
# Usage: ./online_file_step2_poll_result.sh <task_id> [output_directory] [max_retries] [retry_interval_seconds]

set -e

# Security functions
validate_dirname() {
    local dir="$1"
    # Prevent directory traversal - disallow .. and absolute paths
    if [[ "$dir" == *".."* ]] || [[ "$dir" == /* ]]; then
        echo "❌ Error: Invalid directory name. Cannot contain '..' or start with '/'"
        exit 1
    fi
    # Limit length
    if [ ${#dir} -gt 255 ]; then
        echo "❌ Error: Directory name too long (max 255 chars)"
        exit 1
    fi
    echo "$dir"
}

# Support MINERU_TOKEN or MINERU_API_KEY environment variables
MINERU_TOKEN="${MINERU_TOKEN:-${MINERU_API_KEY:-}}"
MINERU_BASE_URL="${MINERU_BASE_URL:-https://mineru.net/api/v4}"

if [ -z "$MINERU_TOKEN" ]; then
    echo "❌ Error: Please set MINERU_TOKEN or MINERU_API_KEY environment variable"
    exit 1
fi

TASK_ID="${1:-}"
if [ -z "$TASK_ID" ]; then
    echo "❌ Error: Please provide task_id"
    echo "Usage: $0 <task_id> [output_directory] [max_retries] [retry_interval_seconds]"
    echo ""
    echo "Example:"
    echo "  $0 xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    exit 1
fi

OUTPUT_DIR="${2:-online_result}"
MAX_RETRIES="${3:-60}"
RETRY_INTERVAL="${4:-5}"

# Validate directory name
OUTPUT_DIR=$(validate_dirname "$OUTPUT_DIR")

echo "=== Step 2: Poll Extraction Results ==="
echo "Task ID: $TASK_ID"
echo "Output Directory: $OUTPUT_DIR"
echo "Max Retries: $MAX_RETRIES"
echo "Retry Interval: $RETRY_INTERVAL seconds"
echo ""
echo "Waiting 5 seconds for system to start processing..."
sleep 5

for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
    echo ""
    echo "[Attempt $attempt/$MAX_RETRIES] $(date '+%H:%M:%S') Querying..."
    
    RESPONSE=$(curl -s -X GET "${MINERU_BASE_URL}/extract/task/${TASK_ID}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${MINERU_TOKEN}")
    
    # Check code
    if command -v jq &> /dev/null; then
        CODE=$(echo "$RESPONSE" | jq -r '.code // 1')
    else
        CODE=$(echo "$RESPONSE" | grep -o '"code":[0-9]*' | head -1 | cut -d':' -f2)
    fi
    
    if [ "$CODE" != "0" ]; then
        echo "⚠️  API Error: $RESPONSE"
        sleep $RETRY_INTERVAL
        continue
    fi
    
    # Parse state
    if command -v jq &> /dev/null; then
        STATE=$(echo "$RESPONSE" | jq -r '.data.state // empty')
    else
        STATE=$(echo "$RESPONSE" | grep -o '"state":"[^"]*"' | head -1 | cut -d'"' -f4)
    fi
    
    echo "Status: $STATE"
    
    case "$STATE" in
        "done")
            echo ""
            echo "✅ Extraction Complete!"
            
            if command -v jq &> /dev/null; then
                ZIP_URL=$(echo "$RESPONSE" | jq -r '.data.full_zip_url // empty')
            else
                ZIP_URL=$(echo "$RESPONSE" | grep -o '"full_zip_url":"[^"]*"' | head -1 | cut -d'"' -f4)
            fi
            
            # Validate ZIP URL
            if [[ ! "$ZIP_URL" =~ ^https://cdn-mineru\.openxlab\.org\.cn/ ]]; then
                echo "❌ Error: Invalid ZIP URL from API"
                exit 1
            fi
            
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "FULL_ZIP_URL=$ZIP_URL"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            
            # Download and extract
            echo "=== Download and Extract Results ==="
            mkdir -p "$OUTPUT_DIR"
            
            ZIP_NAME="result.zip"
            echo "📥 Downloading..."
            curl -L -o "${OUTPUT_DIR}/${ZIP_NAME}" "$ZIP_URL"
            
            # Validate ZIP
            if ! unzip -t "${OUTPUT_DIR}/${ZIP_NAME}" &>/dev/null; then
                echo "❌ Error: Invalid ZIP file downloaded"
                exit 1
            fi
            
            echo "📦 Extracting..."
            unzip -q "${OUTPUT_DIR}/${ZIP_NAME}" -d "${OUTPUT_DIR}/extracted"
            
            echo ""
            echo "✅ Complete! Results saved to: $OUTPUT_DIR/extracted/"
            echo ""
            echo "Key files:"
            echo "  📄 $OUTPUT_DIR/extracted/full.md - Markdown document"
            echo "  🖼️  $OUTPUT_DIR/extracted/images/ - Extracted images"
            exit 0
            ;;
        "failed")
            if command -v jq &> /dev/null; then
                ERR_MSG=$(echo "$RESPONSE" | jq -r '.data.err_msg // "Unknown error"')
            else
                ERR_MSG=$(echo "$RESPONSE" | grep -o '"err_msg":"[^"]*"' | head -1 | cut -d'"' -f4)
            fi
            echo ""
            echo "❌ Extraction Failed: $ERR_MSG"
            exit 1
            ;;
        "running"|"pending")
            echo "Processing... Waiting ${RETRY_INTERVAL} seconds"
            sleep $RETRY_INTERVAL
            ;;
        *)
            echo "Unknown status, continuing to wait..."
            sleep $RETRY_INTERVAL
            ;;
    esac
done

echo ""
echo "❌ Polling timeout, waited $((MAX_RETRIES * RETRY_INTERVAL)) seconds"
exit 1
