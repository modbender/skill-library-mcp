#!/usr/bin/env bash
set -euo pipefail

# shelv-upload.sh — Upload a PDF to Shelv and create a new shelf
# Usage:
#   shelv-upload.sh <file> [--name <name>] [--template <template>] [--review] [--wait]
#
# Environment:
#   SHELV_API_KEY   (required) API key from shelv.dev

SHELV_API_KEY="${SHELV_API_KEY:-}"
API_URL="https://api.shelv.dev"

FILE_PATH=""
SHELF_NAME=""
TEMPLATE=""
REVIEW=""
WAIT=false
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
  cat >&2 <<'EOF'
Usage: shelv-upload.sh <file> [options]

Upload a PDF document to create a new shelf.

Options:
  --name <name>         Display name for the shelf
  --template <template> Structuring template: book, legal-contract, academic-paper
  --review              Pause in review status before finalizing
  --wait                Wait for processing to complete (chains into shelv-poll-status.sh)

Environment:
  SHELV_API_KEY   Required. Your Shelv API key.
EOF
  exit 1
}

# Parse arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --name)
      SHELF_NAME="$2"
      shift 2
      ;;
    --template)
      TEMPLATE="$2"
      shift 2
      ;;
    --review)
      REVIEW="true"
      shift
      ;;
    --wait)
      WAIT=true
      shift
      ;;
    --help|-h)
      usage
      ;;
    -*)
      echo "Error: Unknown flag: $1" >&2
      usage
      ;;
    *)
      if [ -z "$FILE_PATH" ]; then
        FILE_PATH="$1"
      else
        echo "Error: Unexpected argument: $1" >&2
        usage
      fi
      shift
      ;;
  esac
done

if [ -z "$FILE_PATH" ]; then
  echo "Error: file path is required" >&2
  usage
fi

if [ ! -f "$FILE_PATH" ]; then
  echo "Error: File not found: $FILE_PATH" >&2
  exit 1
fi

if [ -z "$SHELV_API_KEY" ]; then
  echo "Error: SHELV_API_KEY environment variable is required" >&2
  echo "Get your API key at https://shelv.dev -> Settings -> API Keys" >&2
  exit 1
fi

for cmd in curl jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: $cmd is required but not found" >&2
    exit 1
  fi
done

# Build curl arguments
CURL_ARGS=(-sS -w "\n%{http_code}" \
  -X POST \
  -H "Authorization: Bearer $SHELV_API_KEY" \
  -F "file=@$FILE_PATH")

if [ -n "$SHELF_NAME" ]; then
  CURL_ARGS+=(-F "name=$SHELF_NAME")
fi

if [ -n "$TEMPLATE" ]; then
  CURL_ARGS+=(-F "template=$TEMPLATE")
fi

if [ -n "$REVIEW" ]; then
  CURL_ARGS+=(-F "review=true")
fi

echo "Uploading $(basename "$FILE_PATH")..." >&2
RESPONSE=$(curl "${CURL_ARGS[@]}" -- "$API_URL/v1/shelves")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "201" ]; then
  echo "Error: Upload failed (HTTP $HTTP_CODE)" >&2
  echo "$BODY" >&2
  exit 1
fi

PUBLIC_ID=$(echo "$BODY" | jq -r '.publicId')
NAME=$(echo "$BODY" | jq -r '.name')

echo "Shelf created: $PUBLIC_ID ($NAME)" >&2
echo "$PUBLIC_ID"

# Optionally wait for processing
if [ "$WAIT" = true ]; then
  echo "" >&2
  echo "Waiting for processing to complete..." >&2
  exec "$SCRIPT_DIR/shelv-poll-status.sh" "$PUBLIC_ID"
fi
