#!/bin/bash
# DeepRead Form Fill — Shell Reference Implementation
#
# Upload a PDF form + JSON data → get back a filled PDF.
#
# Only contacts: api.deepread.tech
# Requires: DEEPREAD_API_KEY environment variable
#
# Usage:
#   ./form_fill.sh <pdf_path> <form_fields_json_string>
#
# Example:
#   ./form_fill.sh application.pdf '{"full_name": "Jane Doe", "dob": "1990-03-15"}'
#
# Dependencies: curl, jq

set -euo pipefail

API_BASE="https://api.deepread.tech"

# --- Validate inputs ---

if [ -z "${DEEPREAD_API_KEY:-}" ]; then
  echo "Error: DEEPREAD_API_KEY is not set." >&2
  echo "Get a free key at https://www.deepread.tech/dashboard" >&2
  exit 1
fi

if [ $# -lt 2 ]; then
  echo "Usage: $0 <pdf_path> '<form_fields_json>'" >&2
  echo "Example: $0 form.pdf '{\"name\": \"Jane Doe\"}'" >&2
  exit 1
fi

PDF_PATH="$1"
FORM_FIELDS="$2"

if [ ! -f "$PDF_PATH" ]; then
  echo "Error: File not found: $PDF_PATH" >&2
  exit 1
fi

# Validate JSON
echo "$FORM_FIELDS" | jq . > /dev/null 2>&1 || {
  echo "Error: Invalid JSON in form_fields." >&2
  exit 1
}

# --- Step 1: Submit form ---

echo "Submitting $(basename "$PDF_PATH")..."
SUBMIT_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/form-fill" \
  -H "X-API-Key: ${DEEPREAD_API_KEY}" \
  -F "file=@${PDF_PATH}" \
  -F "form_fields=${FORM_FIELDS}")

JOB_ID=$(echo "$SUBMIT_RESPONSE" | jq -r '.id // empty')

if [ -z "$JOB_ID" ]; then
  echo "Error: Failed to submit form." >&2
  echo "Response: $SUBMIT_RESPONSE" >&2
  exit 1
fi

STATUS=$(echo "$SUBMIT_RESPONSE" | jq -r '.status')
echo "Job ${JOB_ID} — status: ${STATUS}"

# --- Step 2: Poll for result ---

echo "Waiting for result..."
while true; do
  RESULT=$(curl -s "${API_BASE}/v1/form-fill/${JOB_ID}" \
    -H "X-API-Key: ${DEEPREAD_API_KEY}")

  STATUS=$(echo "$RESULT" | jq -r '.status')

  if [ "$STATUS" = "completed" ]; then
    break
  elif [ "$STATUS" = "failed" ]; then
    ERROR=$(echo "$RESULT" | jq -r '.error_message // "Unknown error"')
    echo "Error: Job failed — ${ERROR}" >&2
    exit 1
  fi

  sleep 5
done

# --- Step 3: Print results ---

FILLED_URL=$(echo "$RESULT" | jq -r '.filled_form_url // "N/A"')
DETECTED=$(echo "$RESULT" | jq -r '.fields_detected // 0')
FILLED=$(echo "$RESULT" | jq -r '.fields_filled // 0')
VERIFIED=$(echo "$RESULT" | jq -r '.fields_verified // 0')
HIL=$(echo "$RESULT" | jq -r '.fields_hil_flagged // 0')
DURATION=$(echo "$RESULT" | jq -r '.duration_seconds // 0')

echo ""
echo "Status: completed"
echo "Fields: ${FILLED}/${DETECTED} filled, ${VERIFIED} verified, ${HIL} need review"
echo "Time: ${DURATION}s"
echo "Download: ${FILLED_URL}"
