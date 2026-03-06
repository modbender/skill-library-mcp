#!/usr/bin/env bash
set -euo pipefail

# S3 Bulk Upload - Upload files with first-character prefix organization
# Usage: s3-bulk-upload.sh <source-dir> <bucket> [--storage-class CLASS] [--dry-run]

usage() {
  cat <<EOF
Usage: $(basename "$0") <source-dir> <bucket> [options]

Upload files to S3 with automatic first-character prefix organization.
  e.g., apple.txt -> a/apple.txt, 123.txt -> 0-9/123.txt

Options:
  --storage-class CLASS   S3 storage class (STANDARD, STANDARD_IA, GLACIER_IR, INTELLIGENT_TIERING)
  --dry-run               Show what would be uploaded without uploading
  --sync                  Use staging + aws s3 sync (faster for many files)
  -h, --help              Show this help message

Examples:
  $(basename "$0") ./files my-bucket
  $(basename "$0") ./files my-bucket --storage-class STANDARD_IA
  $(basename "$0") ./files my-bucket --dry-run
  $(basename "$0") ./files my-bucket --sync
EOF
  exit 1
}

# Compute prefix from filename
get_prefix() {
  local filename="$1"
  local first_char
  first_char=$(echo "$filename" | cut -c1 | tr '[:upper:]' '[:lower:]')

  if [[ "$first_char" =~ [a-z] ]]; then
    echo "$first_char"
  elif [[ "$first_char" =~ [0-9] ]]; then
    echo "0-9"
  else
    echo "_other"
  fi
}

# Parse arguments
SOURCE_DIR=""
BUCKET=""
STORAGE_CLASS=""
DRY_RUN=false
USE_SYNC=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --storage-class)
      STORAGE_CLASS="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --sync)
      USE_SYNC=true
      shift
      ;;
    -h|--help)
      usage
      ;;
    -*)
      echo "Error: Unknown option $1" >&2
      usage
      ;;
    *)
      if [[ -z "$SOURCE_DIR" ]]; then
        SOURCE_DIR="$1"
      elif [[ -z "$BUCKET" ]]; then
        BUCKET="$1"
      else
        echo "Error: Unexpected argument $1" >&2
        usage
      fi
      shift
      ;;
  esac
done

# Validate required arguments
if [[ -z "$SOURCE_DIR" || -z "$BUCKET" ]]; then
  echo "Error: source-dir and bucket are required" >&2
  usage
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Error: Source directory does not exist: $SOURCE_DIR" >&2
  exit 1
fi

# Build storage class flag
STORAGE_FLAG=""
if [[ -n "$STORAGE_CLASS" ]]; then
  STORAGE_FLAG="--storage-class $STORAGE_CLASS"
fi

# Count files
FILE_COUNT=$(find "$SOURCE_DIR" -maxdepth 1 -type f | wc -l | tr -d ' ')
echo "Found $FILE_COUNT files in $SOURCE_DIR"

if [[ "$FILE_COUNT" -eq 0 ]]; then
  echo "No files to upload"
  exit 0
fi

# Upload using sync method (staging directory)
upload_sync() {
  local staging_dir
  staging_dir=$(mktemp -d)
  trap 'rm -rf "$staging_dir"' EXIT

  echo "Creating staging directory structure..."

  for file in "$SOURCE_DIR"/*; do
    [[ -f "$file" ]] || continue
    local basename
    basename=$(basename "$file")
    local prefix
    prefix=$(get_prefix "$basename")

    mkdir -p "$staging_dir/$prefix"
    ln -s "$(realpath "$file")" "$staging_dir/$prefix/$basename"
  done

  if $DRY_RUN; then
    echo "[DRY RUN] Would sync to s3://$BUCKET/"
    find "$staging_dir" -type l -exec echo "  {}" \;
  else
    echo "Syncing to s3://$BUCKET/..."
    # shellcheck disable=SC2086
    aws s3 sync "$staging_dir" "s3://$BUCKET/" $STORAGE_FLAG
  fi
}

# Upload files one by one
upload_individual() {
  local uploaded=0
  local failed=0

  for file in "$SOURCE_DIR"/*; do
    [[ -f "$file" ]] || continue
    local basename
    basename=$(basename "$file")
    local prefix
    prefix=$(get_prefix "$basename")
    local dest="s3://$BUCKET/$prefix/$basename"

    if $DRY_RUN; then
      echo "[DRY RUN] $file -> $dest"
    else
      echo "Uploading: $basename -> $prefix/$basename"
      # shellcheck disable=SC2086
      if aws s3 cp "$file" "$dest" $STORAGE_FLAG --quiet; then
        ((uploaded++))
      else
        echo "  Failed: $basename" >&2
        ((failed++))
      fi
    fi
  done

  if ! $DRY_RUN; then
    echo ""
    echo "Complete: $uploaded uploaded, $failed failed"
  fi
}

# Run upload
if $USE_SYNC; then
  upload_sync
else
  upload_individual
fi
