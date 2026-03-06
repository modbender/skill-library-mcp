#!/bin/bash
# Extract attachments from a note (scanned documents/images)
# Usage: notes-attachment.sh <note-name> [folder] [output-dir]
# Default output-dir: /tmp/notes-export/

source "$(dirname "$0")/_resolve_folder.sh"

NAME="${1:-}"
FOLDER="${2:-}"
OUTPUT_DIR="${3:-/tmp/notes-export/}"

if [ -z "$NAME" ]; then
    echo "Usage: notes-attachment.sh <note-name> [folder] [output-dir]"
    exit 1
fi

# Auto-detect Notes account UUID
ACCOUNTS_DIR="$HOME/Library/Group Containers/group.com.apple.notes/Accounts/"
if [ ! -d "$ACCOUNTS_DIR" ]; then
    echo "Error: Notes accounts directory not found" >&2
    exit 1
fi

ACCOUNT_UUID=$(ls -1 "$ACCOUNTS_DIR" 2>/dev/null | grep -iE '^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$' | head -1)
if [ -z "$ACCOUNT_UUID" ]; then
    echo "Error: Could not auto-detect Notes account UUID" >&2
    exit 1
fi

FALLBACK_BASE="$ACCOUNTS_DIR/$ACCOUNT_UUID/FallbackPDFs"
PREVIEW_BASE="$ACCOUNTS_DIR/$ACCOUNT_UUID/Previews"

ESCAPED_NAME="$(escape_as "$NAME")"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# ID lookup (direct)
if [[ "$NAME" == x-coredata* ]]; then
    ATTACHMENT_INFO=$(osascript <<EOF
tell application "Notes"
    try
        set n to note id "$ESCAPED_NAME"
        set noteTitle to name of n
        set noteFolder to "unknown"
        try
            set noteFolder to name of container of n
        end try
        set attachmentList to {}
        repeat with a in attachments of n
            try
                set contentId to content identifier of a
                set attachmentList to attachmentList & {contentId}
            end try
        end repeat
        return noteTitle & "|" & noteFolder & "|" & (count of attachmentList) & "|" & (attachmentList as string)
    on error errMsg
        return "ERROR:" & errMsg
    end try
end tell
EOF
)
else
    # Name lookup with folder
    resolve_folder "$FOLDER"
    
    ATTACHMENT_INFO=$(osascript <<EOF
tell application "Notes"
    try
        $FOLDER_SCRIPT
    on error errMsg
        return "ERROR:" & errMsg
    end try
    
    set searchTerm to "$ESCAPED_NAME" as text
    repeat with n in noteList
        if name of n contains searchTerm then
            set noteTitle to name of n
            set noteFolder to "unknown"
            try
                set noteFolder to name of container of n
            end try
            set attachmentList to {}
            repeat with a in attachments of n
                try
                    set contentId to content identifier of a
                    set attachmentList to attachmentList & {contentId}
                end try
            end repeat
            return noteTitle & "|" & noteFolder & "|" & (count of attachmentList) & "|" & (attachmentList as string)
        end if
    end repeat
    return "ERROR:No note matching '" & searchTerm & "' found"
end tell
EOF
)
fi

if [[ "$ATTACHMENT_INFO" == ERROR:* ]]; then
    echo "Error: ${ATTACHMENT_INFO#ERROR:}" >&2
    exit 1
fi

# Parse attachment info
IFS='|' read -r NOTE_TITLE NOTE_FOLDER ATTACHMENT_COUNT ATTACHMENT_IDS <<< "$ATTACHMENT_INFO"

echo "Note: $NOTE_TITLE"
echo "Folder: $NOTE_FOLDER"
echo "Attachments found: $ATTACHMENT_COUNT"
echo "---"

if [ "$ATTACHMENT_COUNT" -eq 0 ]; then
    echo "No attachments found in this note."
    exit 0
fi

# Convert attachment IDs to array (comma-separated from AppleScript)
IFS=',' read -ra ID_ARRAY <<< "$ATTACHMENT_IDS"

EXTRACTED_COUNT=0

for content_id in "${ID_ARRAY[@]}"; do
    # Trim whitespace
    content_id=$(echo "$content_id" | xargs)
    # Strip cid: prefix and @icloud.apple.com suffix
    content_id=$(echo "$content_id" | sed 's/^cid://; s/@.*$//')
    
    # Clean up content ID for filename (remove UUID-like parts)
    clean_name=$(echo "$content_id" | sed 's/^[0-9A-F]\{8\}-[0-9A-F]\{4\}-[0-9A-F]\{4\}-[0-9A-F]\{4\}-[0-9A-F]\{12\}\///; s/\//-/g')
    
    # Try to find FallbackPDF first (scanned documents)
    FOUND_FILE=""
    
    # Check for FallbackPDF
    if [ -d "$FALLBACK_BASE/$content_id" ]; then
        pdf_path=$(find "$FALLBACK_BASE/$content_id" -name "FallbackPDF.pdf" 2>/dev/null | head -1)
        if [ -n "$pdf_path" ] && [ -f "$pdf_path" ]; then
            FOUND_FILE="$pdf_path"
            ext="pdf"
        fi
    fi
    
    # Look for preview images if no PDF
    if [ -z "$FOUND_FILE" ] && [ -d "$PREVIEW_BASE" ]; then
        preview_files=$(find "$PREVIEW_BASE" -name "$content_id-*.png" 2>/dev/null)
        if [ -n "$preview_files" ]; then
            # Get the largest preview file
            FOUND_FILE=$(ls -S $preview_files 2>/dev/null | head -1)
            ext="png"
        fi
    fi
    
    if [ -n "$FOUND_FILE" ]; then
        # Create sanitized filename
        safe_title=$(echo "$NOTE_TITLE" | tr -cd '[:alnum:]._-' | cut -c1-50)
        output_filename="${safe_title}-${EXTRACTED_COUNT}.${ext}"
        output_path="$OUTPUT_DIR/$output_filename"
        
        # Handle duplicates
        counter=1
        while [ -f "$output_path" ]; do
            output_filename="${safe_title}-${EXTRACTED_COUNT}(${counter}).${ext}"
            output_path="$OUTPUT_DIR/$output_filename"
            counter=$((counter + 1))
        done
        
        cp "$FOUND_FILE" "$output_path"
        echo "Extracted: $output_path"
        EXTRACTED_COUNT=$((EXTRACTED_COUNT + 1))
    else
        echo "Warning: Could not locate file for attachment: $content_id" >&2
    fi
done

echo "---"
echo "Total extracted: $EXTRACTED_COUNT"
