#!/usr/bin/env bash
set -euo pipefail

API_KEY="${WORTHCLIP_API_KEY:?Set WORTHCLIP_API_KEY}"
BASE="https://greedy-mallard-11.convex.site/api/v1"

VIDEO_ID="${1:?Usage: score.sh VIDEO_ID}"

# Validate VIDEO_ID is alphanumeric/dash/underscore only (YouTube video ID format)
if [[ ! "$VIDEO_ID" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "Invalid video ID: must be alphanumeric, dash, or underscore only" >&2
  exit 1
fi

# Build JSON payload safely with jq
PAYLOAD=$(jq -n --arg vid "$VIDEO_ID" '{"youtubeVideoId": $vid}')

# Submit scoring request
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST "$BASE/score" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

# If already scored (200), print and exit
if [ "$HTTP_CODE" = "200" ]; then
  echo "$BODY" | jq '.data'
  exit 0
fi

# If accepted (202), poll for completion
if [ "$HTTP_CODE" = "202" ]; then
  JOB_ID=$(echo "$BODY" | jq -r '.data.jobId')

  # Validate job ID before using in URL
  if [[ ! "$JOB_ID" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Invalid job ID returned" >&2
    exit 1
  fi

  echo "Scoring started, polling job $JOB_ID..." >&2

  for i in $(seq 1 30); do
    sleep 2
    POLL=$(curl -s -w "\n%{http_code}" \
      "$BASE/score/$JOB_ID" \
      -H "Authorization: Bearer $API_KEY")
    POLL_CODE=$(echo "$POLL" | tail -1)
    POLL_BODY=$(echo "$POLL" | sed '$d')

    STATUS=$(echo "$POLL_BODY" | jq -r '.data.status // empty')

    if [ "$POLL_CODE" = "200" ] && [ "$STATUS" = "completed" ]; then
      echo "$POLL_BODY" | jq '.data'
      exit 0
    fi

    if [ "$POLL_CODE" = "500" ]; then
      echo "Scoring failed: $(echo "$POLL_BODY" | jq -r '.error.message')" >&2
      exit 1
    fi

    echo "  Status: $STATUS (attempt $i/30)" >&2
  done

  echo "Timeout: scoring did not complete within 60 seconds" >&2
  exit 1
fi

# Error response
echo "$BODY" | jq '.error' >&2
exit 1
