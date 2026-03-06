#!/bin/bash
# MinerU Local File Parsing Step 3: Poll Extraction Results
# Usage: ./local_file_step3_poll_result.sh <batch_id> [max_retries] [retry_interval_seconds]

set -e

# Support MINERU_TOKEN or MINERU_API_KEY environment variables
MINERU_TOKEN="${MINERU_TOKEN:-${MINERU_API_KEY:-}}"
MINERU_BASE_URL="${MINERU_BASE_URL:-https://mineru.net/api/v4}"

if [ -z "$MINERU_TOKEN" ]; then
    echo "❌ Error: Please set MINERU_TOKEN or MINERU_API_KEY environment variable"
    exit 1
fi

BATCH_ID="${1:-}"
if [ -z "$BATCH_ID" ]; then
    echo "❌ Error: Please provide batch_id"
    echo "Usage: $0 <batch_id> [max_retries] [retry_interval_seconds]"
    echo ""
    echo "Example:"
    echo "  $0 xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    exit 1
fi

MAX_RETRIES="${2:-60}"
RETRY_INTERVAL="${3:-5}"

echo "=== Step 3: Poll Extraction Results ==="
echo "Batch ID: $BATCH_ID"
echo "Max Retries: $MAX_RETRIES"
echo "Retry Interval: $RETRY_INTERVAL seconds"
echo ""
echo "Waiting 5 seconds for system to start processing..."
sleep 5

for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
    echo ""
    echo "[Attempt $attempt/$MAX_RETRIES] $(date '+%H:%M:%S') Querying..."
    
    RESPONSE=$(curl -s -X GET "${MINERU_BASE_URL}/extract-results/batch/${BATCH_ID}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${MINERU_TOKEN}")
    
    # Check code
    CODE=$(echo "$RESPONSE" | grep -o '"code":[0-9]*' | cut -d':' -f2)
    if [ "$CODE" != "0" ]; then
        echo "⚠️ API Error: $RESPONSE"
        sleep $RETRY_INTERVAL
        continue
    fi
    
    # Parse state
    STATE=$(echo "$RESPONSE" | grep -o '"state":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Status: $STATE"
    
    case "$STATE" in
        "done")
            echo ""
            echo "✅ Extraction Complete!"
            ZIP_URL=$(echo "$RESPONSE" | grep -o '"full_zip_url":"[^"]*"' | head -1 | cut -d'"' -f4)
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "FULL_ZIP_URL=$ZIP_URL"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "💡 Next Step: Execute Step 4 to download results"
            echo "   ./local_file_step4_download.sh \"$ZIP_URL\" \"output.zip\" \"extracted_folder\""
            exit 0
            ;;
        "failed")
            ERR_MSG=$(echo "$RESPONSE" | grep -o '"err_msg":"[^"]*"' | head -1 | cut -d'"' -f4)
            echo ""
            echo "❌ Extraction Failed: $ERR_MSG"
            exit 1
            ;;
        "running"|"waiting-file"|"pending"|"converting")
            echo "Processing... Waiting ${RETRY_INTERVAL} seconds"
            sleep $RETRY_INTERVAL
            ;;
        *)
            echo "Unknown status: $STATE"
            echo "Waiting ${RETRY_INTERVAL} seconds..."
            sleep $RETRY_INTERVAL
            ;;
    esac
done

echo ""
echo "❌ Polling timeout, waited $((MAX_RETRIES * RETRY_INTERVAL)) seconds"
exit 1
