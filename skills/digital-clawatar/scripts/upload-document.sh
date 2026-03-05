#!/bin/bash
# UNITH API - Upload Knowledge Document
# Uploads a document to a doc_qa digital human's knowledge base.
#
# Requires: UNITH_TOKEN (run: source scripts/auth.sh)
#
# Usage:
#   bash scripts/upload-document.sh <headId> <file_path>
#
# Supported file types: PDF and other document formats accepted by UNITH.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_utils.sh"

check_deps || exit 1
require_token || exit 1

HEAD_ID="${1:-}"
FILE_PATH="${2:-}"

# --- Validate input ---
if [ -z "$HEAD_ID" ] || [ -z "$FILE_PATH" ]; then
  log_error "Both head ID and file path are required."
  echo ""
  echo "Usage: $0 <headId> <file_path>"
  echo ""
  echo "  headId     - The digital human ID (from create-head.sh or list-resources.sh heads)"
  echo "  file_path  - Path to the document file (PDF, etc.)"
  echo ""
  echo "Example: $0 abc123def456 ./knowledge-base.pdf"
  exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
  log_error "File not found: $FILE_PATH"
  exit 1
fi

# --- Check file size ---
FILE_SIZE=$(stat -f%z "$FILE_PATH" 2>/dev/null || stat -c%s "$FILE_PATH" 2>/dev/null || echo "0")
FILE_NAME=$(basename "$FILE_PATH")

if [ "$FILE_SIZE" -eq 0 ]; then
  log_error "File is empty: $FILE_PATH"
  exit 1
fi

FILE_SIZE_MB=$((FILE_SIZE / 1024 / 1024))
if [ "$FILE_SIZE_MB" -gt 50 ]; then
  log_warn "File is ${FILE_SIZE_MB}MB. Large files may take longer to process."
  log_warn "UNITH may have upload size limits — check your plan if the upload fails."
fi

log_info "Uploading '$FILE_NAME' (${FILE_SIZE_MB}MB) to head '$HEAD_ID'..."

# Use a longer timeout for file uploads
CURL_TIMEOUT=120

if ! unith_curl -X POST "$API_BASE/document/upload" \
  -H "Authorization: Bearer $UNITH_TOKEN" \
  -F "file=@$FILE_PATH" \
  -F "headId=$HEAD_ID"; then
  parse_api_error "$CURL_BODY"
  log_error "Document upload failed."
  log_error ""
  case "$CURL_HTTP_CODE" in
    400)
      log_error "Likely causes:"
      log_error "  - Unsupported file format"
      log_error "  - Head ID '$HEAD_ID' is not a doc_qa digital human"
      ;;
    404)
      log_error "Head '$HEAD_ID' not found."
      log_error "Check your heads with: bash scripts/list-resources.sh heads"
      ;;
    413)
      log_error "File too large. Try a smaller document or contact UNITH support."
      ;;
  esac
  exit 1
fi

log_ok "Document uploaded successfully to head '$HEAD_ID'."
echo ""
log_info "UNITH will auto-generate suggested questions from the document."
log_info "Review and update them with:"
echo "  bash scripts/list-resources.sh head $HEAD_ID"
echo ""
log_info "To update suggestions manually, use PUT /head/update with:"
echo "  {\"id\":\"$HEAD_ID\", \"suggestions\":\"[\\\"Question 1?\\\",\\\"Question 2?\\\"]\"}"
