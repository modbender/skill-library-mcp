#!/usr/bin/env bash
set -euo pipefail

# shelv-hydrate.sh — Download a shelf archive and extract it into the OpenClaw workspace
# Usage:
#   shelv-hydrate.sh <shelf-public-id> [--name <name>] [--force]
#
# Environment:
#   SHELV_API_KEY   (required) API key from shelv.dev

SHELV_API_KEY="${SHELV_API_KEY:-}"
API_URL="https://api.shelv.dev"
WORKSPACE="${HOME}/.openclaw/workspace/shelves"

SHELF_ID=""
SHELF_NAME=""
FORCE=false

usage() {
  cat >&2 <<'EOF'
Usage: shelv-hydrate.sh <shelf-public-id> [--name <name>] [--force]

Downloads a shelf archive and extracts it into ~/.openclaw/workspace/shelves/<name>/

Options:
  --name <name>   Override the directory name (default: derived from shelf metadata)
  --force         Replace existing directory if it already exists

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
    --force)
      FORCE=true
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
      if [ -z "$SHELF_ID" ]; then
        SHELF_ID="$1"
      else
        echo "Error: Unexpected argument: $1" >&2
        usage
      fi
      shift
      ;;
  esac
done

if [ -z "$SHELF_ID" ]; then
  echo "Error: shelf-public-id is required" >&2
  usage
fi

if [ -z "$SHELV_API_KEY" ]; then
  echo "Error: SHELV_API_KEY environment variable is required" >&2
  echo "Get your API key at https://shelv.dev -> Settings -> API Keys" >&2
  exit 1
fi

# Preflight checks
for cmd in curl tar jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: $cmd is required but not found" >&2
    exit 1
  fi
done

# Require sha256 tool
SHA256_CMD=""
if command -v sha256sum >/dev/null 2>&1; then
  SHA256_CMD="sha256sum"
elif command -v shasum >/dev/null 2>&1; then
  SHA256_CMD="shasum -a 256"
else
  echo "Error: sha256sum or shasum is required but not found" >&2
  exit 1
fi

# If no name provided, fetch shelf metadata to derive one
if [ -z "$SHELF_NAME" ]; then
  echo "Fetching shelf metadata..." >&2
  META_RESPONSE=$(curl -sS -w "\n%{http_code}" \
    -H "Authorization: Bearer $SHELV_API_KEY" \
    -- "$API_URL/v1/shelves/$SHELF_ID")

  META_HTTP=$(echo "$META_RESPONSE" | tail -n1)
  META_BODY=$(echo "$META_RESPONSE" | sed '$d')

  if [ "$META_HTTP" != "200" ]; then
    echo "Error: Failed to fetch shelf metadata (HTTP $META_HTTP)" >&2
    echo "$META_BODY" >&2
    exit 1
  fi

  # Derive name from shelf metadata
  RAW_NAME=$(echo "$META_BODY" | jq -r '.name // empty')
  if [ -z "$RAW_NAME" ]; then
    RAW_NAME="$SHELF_ID"
  fi

  # Sanitize: lowercase, replace spaces/special chars with hyphens, strip leading/trailing hyphens
  SHELF_NAME=$(echo "$RAW_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
fi

# Sanitize --name override (same rules as API-derived name)
SHELF_NAME=$(echo "$SHELF_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')

if [ -z "$SHELF_NAME" ]; then
  echo "Error: Shelf name is empty after sanitization" >&2
  exit 1
fi

TARGET="$WORKSPACE/$SHELF_NAME"

# Verify target is inside workspace (prevent path traversal)
mkdir -p "$WORKSPACE"
REAL_WORKSPACE=$(cd "$WORKSPACE" 2>/dev/null && pwd)
case "$TARGET" in
  "$REAL_WORKSPACE"/*) ;; # safe
  *) echo "Error: Target path escapes workspace" >&2; exit 1 ;;
esac

# Handle collision
if [ -d "$TARGET" ]; then
  if [ "$FORCE" != true ]; then
    echo "Error: $TARGET already exists. Use --force to replace it." >&2
    exit 1
  fi
  echo "Warning: $TARGET already exists, replacing (--force)..." >&2
  rm -rf "${TARGET:?}"
fi

# Temp dir with cleanup trap
TMPDIR_DOWNLOAD="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_DOWNLOAD"' EXIT

# Fetch archive URL with retry loop for 202
MAX_RETRIES=30
RETRY_COUNT=0

echo "Requesting archive URL..." >&2
while true; do
  RESPONSE=$(curl -sS -w "\n%{http_code}" \
    -H "Authorization: Bearer $SHELV_API_KEY" \
    -- "$API_URL/v1/shelves/$SHELF_ID/archive-url")

  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  BODY=$(echo "$RESPONSE" | sed '$d')

  if [ "$HTTP_CODE" = "200" ]; then
    break
  elif [ "$HTTP_CODE" = "202" ]; then
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
      echo "Error: Archive generation timed out after $MAX_RETRIES retries" >&2
      exit 1
    fi
    RETRY_AFTER=$(echo "$BODY" | jq -r '.retryAfter // 5')
    echo "Archive generating, retrying in ${RETRY_AFTER}s..." >&2
    sleep "$RETRY_AFTER"
  else
    echo "Error: API returned HTTP $HTTP_CODE" >&2
    echo "$BODY" >&2
    exit 1
  fi
done

# Extract fields from JSON response
ARCHIVE_URL=$(echo "$BODY" | jq -r '.url')
EXPECTED_SHA=$(echo "$BODY" | jq -r '.sha256 // empty')

if [ -z "$ARCHIVE_URL" ] || [ "$ARCHIVE_URL" = "null" ]; then
  echo "Error: Could not parse archive URL from response" >&2
  exit 1
fi

# Download archive
ARCHIVE_FILE="$TMPDIR_DOWNLOAD/archive.tar.gz"
echo "Downloading archive..." >&2
curl -sS --retry 3 --retry-delay 2 --max-time 120 -o "$ARCHIVE_FILE" -- "$ARCHIVE_URL"

# Verify checksum (mandatory)
if [ -z "$EXPECTED_SHA" ]; then
  echo "Error: API response missing required sha256 checksum" >&2
  exit 1
fi

ACTUAL_SHA=$($SHA256_CMD "$ARCHIVE_FILE" | cut -d' ' -f1)
if [ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]; then
  echo "Error: Checksum mismatch" >&2
  echo "  Expected: $EXPECTED_SHA" >&2
  echo "  Actual:   $ACTUAL_SHA" >&2
  exit 1
fi
echo "Checksum verified." >&2

# Extract to temp, then move to target
EXTRACT_DIR="$TMPDIR_DOWNLOAD/extract"
mkdir -p "$EXTRACT_DIR"

# Check for path traversal in archive entries
if tar tzf "$ARCHIVE_FILE" | grep -qE '(^|/)\.\.(/|$)|^/'; then
  echo "Error: Archive contains unsafe path entries" >&2
  exit 1
fi

# Reject archives containing symlinks (symlinks could point outside workspace)
if tar tvf "$ARCHIVE_FILE" | grep -q '^l'; then
  echo "Error: Archive contains symlinks, which are not allowed" >&2
  exit 1
fi

tar xzf "$ARCHIVE_FILE" -C "$EXTRACT_DIR"

# Move to workspace
mkdir -p "$WORKSPACE"
mv "$EXTRACT_DIR" "$TARGET"

echo "" >&2
echo "Shelf hydrated to $TARGET" >&2
echo "" >&2

# Print file listing so the agent sees the structure
echo "Files:"
find "$TARGET" -type f | sort | while read -r f; do
  echo "  ${f#"$TARGET"/}"
done
