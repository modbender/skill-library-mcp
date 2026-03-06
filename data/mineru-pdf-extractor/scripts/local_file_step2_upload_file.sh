#!/bin/bash
# MinerU Local File Parsing Step 2: Upload File
# Usage: ./local_file_step2_upload_file.sh <upload_url> <pdf_file_path>

set -e

UPLOAD_URL="${1:-}"
PDF_PATH="${2:-}"

if [ -z "$UPLOAD_URL" ] || [ -z "$PDF_PATH" ]; then
    echo "❌ Error: Insufficient parameters"
    echo "Usage: $0 <upload_url> <pdf_file_path>"
    echo ""
    echo "Example:"
    echo "  $0 \"https://mineru.oss-cn-shanghai.aliyuncs.com/...\" \"/path/to/file.pdf\""
    exit 1
fi

if [ ! -f "$PDF_PATH" ]; then
    echo "❌ Error: PDF file does not exist: $PDF_PATH"
    exit 1
fi

FILENAME=$(basename "$PDF_PATH")
echo "=== Step 2: Upload File ==="
echo "File: $FILENAME"
echo "Size: $(du -h "$PDF_PATH" | cut -f1)"
echo ""

curl -X PUT "$UPLOAD_URL" --upload-file "$PDF_PATH"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ File uploaded successfully"
    echo ""
    echo "💡 Next Step: Execute Step 3 to poll results"
    echo "   Use the BATCH_ID from Step 1"
else
    echo ""
    echo "❌ File upload failed"
    exit 1
fi
