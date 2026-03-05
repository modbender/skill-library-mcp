#!/bin/bash
# MinerU Local File Parsing Step 4: Download and Extract Results (Secure Version)
# Usage: ./local_file_step4_download.sh <zip_url> [output_zip_filename] [extract_directory_name]

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

sanitize_filename() {
    local name="$1"
    # Only allow safe characters
    name=$(echo "$name" | tr -cd 'a-zA-Z0-9._-')
    # Limit length
    if [ ${#name} -gt 255 ]; then
        name="${name:0:255}"
    fi
    echo "$name"
}

ZIP_URL="${1:-}"
if [ -z "$ZIP_URL" ]; then
    echo "❌ Error: Please provide ZIP download URL"
    exit 1
fi

# Validate URL format
if [[ ! "$ZIP_URL" =~ ^https://cdn-mineru\.openxlab\.org\.cn/ ]]; then
    echo "❌ Error: Invalid ZIP URL. Must be from cdn-mineru.openxlab.org.cn"
    exit 1
fi

ZIP_FILENAME="${2:-result.zip}"
EXTRACT_DIR="${3:-extracted}"

# Sanitize inputs
ZIP_FILENAME=$(sanitize_filename "$ZIP_FILENAME")
EXTRACT_DIR=$(validate_dirname "$EXTRACT_DIR")

echo "=== Step 4: Download and Extract Results ==="
echo "ZIP URL: ${ZIP_URL:0:60}..."
echo "Output File: $ZIP_FILENAME"
echo "Extract Directory: $EXTRACT_DIR"
echo ""

# Create secure working directory
WORK_DIR="$(pwd)"
EXTRACT_PATH="$WORK_DIR/$EXTRACT_DIR"

# Ensure directory is within working directory
if [[ ! "$EXTRACT_PATH" =~ ^"$WORK_DIR" ]]; then
    echo "❌ Error: Extract path escapes working directory"
    exit 1
fi

# Download ZIP
echo "📥 Downloading..."
curl -L -o "$ZIP_FILENAME" "$ZIP_URL"

if [ ! -f "$ZIP_FILENAME" ]; then
    echo "❌ Download failed"
    exit 1
fi

# Validate ZIP file
if ! unzip -t "$ZIP_FILENAME" &>/dev/null; then
    echo "❌ Error: Invalid ZIP file"
    rm -f "$ZIP_FILENAME"
    exit 1
fi

echo "✅ Download complete: $ZIP_FILENAME ($(du -h "$ZIP_FILENAME" | cut -f1))"
echo ""

# Extract
echo "📦 Extracting..."
mkdir -p "$EXTRACT_DIR"
unzip -q "$ZIP_FILENAME" -d "$EXTRACT_DIR"

# Verify extraction result
if [ ! -d "$EXTRACT_DIR" ]; then
    echo "❌ Extraction failed"
    exit 1
fi

echo "✅ Extraction complete: $EXTRACT_DIR/"
echo ""

# Show contents
echo "📁 Extracted files:"
ls -lh "$EXTRACT_DIR/"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 All Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Key files:"
echo "  📄 $EXTRACT_DIR/full.md - Markdown document"
echo "  🖼️  $EXTRACT_DIR/images/ - Extracted images"
