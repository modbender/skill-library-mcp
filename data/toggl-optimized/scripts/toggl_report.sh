#!/bin/bash

# Config
# Note: Set TOGGL_API_TOKEN and TOGGL_WORKSPACE_ID environment variables.
# This script is a template. Customize the client IDs as needed.

API_TOKEN="${TOGGL_API_TOKEN}"
WORKSPACE_ID="${TOGGL_WORKSPACE_ID}"

CLIENT_NAME=$1
START_DATE=$2
END_DATE=$3
FORMAT=$4 # json o pdf

# Map your client names to their respective IDs here
# if [[ "$CLIENT_NAME" == "example" ]]; then
#     CLIENT_ID=12345678
# fi

if [[ -z "$CLIENT_ID" ]]; then
    echo '{"error": "Client ID not found for: '$CLIENT_NAME'. Please map it in the script."}'
    exit 1
fi

URL="https://api.track.toggl.com/reports/api/v3/workspace/$WORKSPACE_ID/summary/time_entries"
[[ "$FORMAT" == "pdf" ]] && URL="${URL}.pdf"

PAYLOAD="{\"client_ids\":[$CLIENT_ID], \"start_date\":\"$START_DATE\", \"end_date\":\"$END_DATE\"}"

if [[ "$FORMAT" == "pdf" ]]; then
    OUTFILE="/tmp/reporte_${CLIENT_NAME}_${START_DATE}_${END_DATE}.pdf"
    curl -s -X POST "$URL" \
         -H "Content-Type: application/json" \
         -u "$API_TOKEN:api_token" \
         -d "$PAYLOAD" \
         --output "$OUTFILE"
    echo "{\"status\": \"ok\", \"file\": \"$OUTFILE\"}"
else
    RESPONSE=$(curl -s -X POST "$URL" \
         -H "Content-Type: application/json" \
         -u "$API_TOKEN:api_token" \
         -d "$PAYLOAD")
    
    TOTAL_SECONDS=$(echo "$RESPONSE" | jq '[.groups[].sub_groups[].seconds] | add')
    HOURS=$((TOTAL_SECONDS / 3600))
    MINUTES=$(( (TOTAL_SECONDS % 3600) / 60 ))
    
    echo "{\"status\": \"ok\", \"total_seconds\": $TOTAL_SECONDS, \"total_formatted\": \"${HOURS}h ${MINUTES}m\"}"
fi
