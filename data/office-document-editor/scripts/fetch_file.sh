#!/bin/bash
# Universal File Fetcher - Handles all file sources
# Usage: bash scripts/fetch_file.sh <source> [output_filename]
#
# Sources:
#   upload         - Latest uploaded file from chat
#   /path/to/file  - Local filesystem path
#   https://...    - Public URL
#   sftp://...     - SFTP remote file

set -e

SOURCE="$1"
OUTPUT="${2:-input.docx}"
WORK_DIR="${3:-.}"

cd "$WORK_DIR"

echo "📥 Fetching file from: $SOURCE"
echo ""

# Function to check if source is a URL
is_url() {
    [[ "$1" =~ ^https?:// ]]
}

# Function to check if source is SFTP
is_sftp() {
    [[ "$1" =~ ^sftp:// ]] || [[ "$1" =~ ^ssh:// ]]
}

# Function to check if source is a local path
is_local_path() {
    [[ -f "$1" ]] || [[ -f "~/$1" ]]
}

# Fetch based on source type
if [ "$SOURCE" = "upload" ] || [ "$SOURCE" = "uploaded" ]; then
    # Get latest uploaded file
    echo "📎 Fetching latest uploaded file..."
    
    # Detect file type from OUTPUT
    if [[ "$OUTPUT" == *.pptx ]]; then
        EXT="pptx"
    else
        EXT="docx"
    fi
    
    LATEST=$(ls -t ~/.openclaw/workspace/media/inbound/file_*.$EXT 2>/dev/null | head -1)
    
    if [ -z "$LATEST" ]; then
        echo "❌ Error: No uploaded files found"
        echo "   Please upload a file first"
        exit 1
    fi
    
    echo "   Found: $(basename "$LATEST")"
    cp "$LATEST" "$OUTPUT"
    echo "✅ Copied to: $WORK_DIR/$OUTPUT"
    
elif is_url "$SOURCE"; then
    # Download from URL
    echo "🌐 Downloading from URL..."
    
    if command -v curl &> /dev/null; then
        curl -L "$SOURCE" -o "$OUTPUT"
    elif command -v wget &> /dev/null; then
        wget -O "$OUTPUT" "$SOURCE"
    else
        echo "❌ Error: Neither curl nor wget found"
        echo "   Please install: sudo apt install curl"
        exit 1
    fi
    
    if [ -f "$OUTPUT" ]; then
        echo "✅ Downloaded to: $WORK_DIR/$OUTPUT"
        echo "   Size: $(du -h "$OUTPUT" | cut -f1)"
    else
        echo "❌ Error: Download failed"
        exit 1
    fi
    
elif is_sftp "$SOURCE"; then
    # Fetch via SFTP
    echo "🔌 Fetching via SFTP..."
    
    # Parse SFTP URL: sftp://user@host:/path/to/file
    SFTP_PATH="${SOURCE#sftp://}"
    SFTP_PATH="${SFTP_PATH#ssh://}"  # Also support ssh://
    
    USER_HOST="${SFTP_PATH%%:*}"
    REMOTE_PATH="${SFTP_PATH#*:}"
    
    echo "   User/Host: $USER_HOST"
    echo "   Remote path: $REMOTE_PATH"
    
    # Create temporary batch file
    BATCH_FILE=$(mktemp)
    cat > "$BATCH_FILE" << EOF
get $REMOTE_PATH $OUTPUT
EOF
    
    # Execute SFTP
    sftp -b "$BATCH_FILE" "$USER_HOST"
    
    rm -f "$BATCH_FILE"
    
    if [ -f "$OUTPUT" ]; then
        echo "✅ Fetched to: $WORK_DIR/$OUTPUT"
    else
        echo "❌ Error: SFTP fetch failed"
        exit 1
    fi
    
elif is_local_path "$SOURCE"; then
    # Copy from local path
    echo "📁 Copying from local path..."
    
    # Expand tilde
    SOURCE="${SOURCE/#\~/$HOME}"
    
    if [ -f "$SOURCE" ]; then
        cp "$SOURCE" "$OUTPUT"
        echo "✅ Copied from: $SOURCE"
        echo "   To: $WORK_DIR/$OUTPUT"
    else
        echo "❌ Error: File not found: $SOURCE"
        exit 1
    fi
    
else
    echo "❌ Error: Unknown source type: $SOURCE"
    echo ""
    echo "Supported sources:"
    echo "  upload         - Latest uploaded file"
    echo "  /path/to/file  - Local filesystem path"
    echo "  https://...    - Public URL"
    echo "  sftp://...     - SFTP remote file"
    echo ""
    echo "Examples:"
    echo "  $0 upload"
    echo "  $0 ~/Documents/report.docx"
    echo "  $0 https://example.com/file.docx"
    echo "  $0 sftp://user@host:/path/file.docx"
    exit 1
fi

echo ""
echo "📊 File info:"
ls -lh "$OUTPUT"
