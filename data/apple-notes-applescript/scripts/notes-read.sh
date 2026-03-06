#!/bin/bash
# Read a note by name (partial match) or by ID
# Usage: notes-read.sh <note-name-or-id> [folder]
# If name starts with "x-coredata" it's treated as an ID lookup
# Shows attachment info at bottom if attachments exist

source "$(dirname "$0")/_resolve_folder.sh"

NAME="${1:-}"
FOLDER="${2:-}"

if [ -z "$NAME" ]; then
    echo "Usage: notes-read.sh <note-name-or-id> [folder]"
    exit 1
fi

ESCAPED_NAME="$(escape_as "$NAME")"

# Auto-detect Notes account UUID for attachment paths
ACCOUNTS_DIR="$HOME/Library/Group Containers/group.com.apple.notes/Accounts/"
ACCOUNT_UUID=""
if [ -d "$ACCOUNTS_DIR" ]; then
    ACCOUNT_UUID=$(ls -1 "$ACCOUNTS_DIR" 2>/dev/null | grep -iE '^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$' | head -1)
fi
FALLBACK_BASE=""
PREVIEW_BASE=""
if [ -n "$ACCOUNT_UUID" ]; then
    FALLBACK_BASE="$ACCOUNTS_DIR/$ACCOUNT_UUID/FallbackPDFs"
    PREVIEW_BASE="$ACCOUNTS_DIR/$ACCOUNT_UUID/Previews"
fi

# Get output dir for extracted files
OUTPUT_DIR="/tmp/notes-export/"
mkdir -p "$OUTPUT_DIR"

# Function to process attachment IDs and output paths
process_attachments() {
    local attachment_data="$1"
    local note_title="$2"
    
    if [ -z "$attachment_data" ] || [ "$attachment_data" = "ATTACHMENT_DATA:" ]; then
        return
    fi
    
    # Remove the prefix
    local ids="${attachment_data#ATTACHMENT_DATA:}"
    
    # Convert comma-separated to array
    IFS=',' read -ra ID_ARRAY <<< "$ids"
    
    local extracted_count=0
    for content_id in "${ID_ARRAY[@]}"; do
        # Trim whitespace
        content_id=$(echo "$content_id" | xargs)
        
        local found_file=""
        local file_type=""
        
        # Check for FallbackPDF
        if [ -n "$FALLBACK_BASE" ] && [ -d "$FALLBACK_BASE/$content_id" ]; then
            local pdf_path=$(find "$FALLBACK_BASE/$content_id" -name "FallbackPDF.pdf" 2>/dev/null | head -1)
            if [ -n "$pdf_path" ] && [ -f "$pdf_path" ]; then
                found_file="$pdf_path"
                file_type="pdf"
            fi
        fi
        
        # Check for preview images
        if [ -z "$found_file" ] && [ -n "$PREVIEW_BASE" ] && [ -d "$PREVIEW_BASE" ]; then
            local preview_files=$(find "$PREVIEW_BASE" -name "$content_id-*.png" 2>/dev/null)
            if [ -n "$preview_files" ]; then
                found_file=$(ls -S $preview_files 2>/dev/null | head -1)
                file_type="png"
            fi
        fi
        
        if [ -n "$found_file" ]; then
            # Create output filename
            local safe_title=$(echo "$note_title" | tr -cd '[:alnum:]._-' | cut -c1-50)
            local output_filename="${safe_title}-${extracted_count}.${file_type}"
            local output_path="$OUTPUT_DIR/$output_filename"
            
            # Handle duplicates
            local counter=1
            while [ -f "$output_path" ]; do
                output_filename="${safe_title}-${extracted_count}(${counter}).${file_type}"
                output_path="$OUTPUT_DIR/$output_filename"
                counter=$((counter + 1))
            done
            
            cp "$found_file" "$output_path"
            echo "  → $output_path"
            extracted_count=$((extracted_count + 1))
        fi
    done
}

# ID lookup — direct, ignores folder
if [[ "$NAME" == x-coredata* ]]; then
    RESULT=$(osascript <<EOF
tell application "Notes"
    try
        set n to note id "$ESCAPED_NAME"
        set noteTitle to name of n
        set noteBody to plaintext of n
        set noteDate to modification date of n
        set noteId to id of n
        try
            set noteFolder to name of container of n
        on error
            set noteFolder to "unknown"
        end try
        
        -- Get attachment info
        set attachmentCount to 0
        set attachmentIds to {}
        repeat with a in attachments of n
            try
                set contentId to content identifier of a
                set attachmentIds to attachmentIds & {contentId}
                set attachmentCount to attachmentCount + 1
            end try
        end repeat
        
        set output to "Title: " & noteTitle & linefeed & "Folder: " & noteFolder & linefeed & "Modified: " & (noteDate as text) & linefeed & "ID: " & noteId & linefeed & "---" & linefeed & noteBody
        
        return output & linefeed & "ATTACHMENT_DATA:" & attachmentCount & "|" & (attachmentIds as string) & "|" & noteTitle
    on error errMsg
        return "Error: " & errMsg
    end try
end tell
EOF
)
else
    # Name lookup — search in folder or all notes
    resolve_folder "$FOLDER"
    
    RESULT=$(osascript <<EOF
tell application "Notes"
    try
        $FOLDER_SCRIPT
    on error errMsg
        return "Error: " & errMsg
    end try
    
    set searchTerm to "$ESCAPED_NAME" as text
    repeat with n in noteList
        if name of n contains searchTerm then
            set noteTitle to name of n
            set noteBody to plaintext of n
            set noteDate to modification date of n
            set noteId to id of n
            try
                set noteFolder to name of container of n
            on error
                set noteFolder to "unknown"
            end try
            
            -- Get attachment info
            set attachmentCount to 0
            set attachmentIds to {}
            repeat with a in attachments of n
                try
                    set contentId to content identifier of a
                    set attachmentIds to attachmentIds & {contentId}
                    set attachmentCount to attachmentCount + 1
                end try
            end repeat
            
            set output to "Title: " & noteTitle & linefeed & "Folder: " & noteFolder & linefeed & "Modified: " & (noteDate as text) & linefeed & "ID: " & noteId & linefeed & "---" & linefeed & noteBody
            
            return output & linefeed & "ATTACHMENT_DATA:" & attachmentCount & "|" & (attachmentIds as string) & "|" & noteTitle
        end if
    end repeat
    return "Error: No note matching '" & searchTerm & "' found"
end tell
EOF
)
fi

# Check for errors
if [[ "$RESULT" == Error:* ]]; then
    echo "$RESULT"
    exit 1
fi

# Split result into content and attachment data
if [[ "$RESULT" == *ATTACHMENT_DATA:* ]]; then
    # Extract attachment section
    ATTACHMENT_SECTION=$(echo "$RESULT" | grep "ATTACHMENT_DATA:")
    # Remove attachment section from main output
    MAIN_OUTPUT=$(echo "$RESULT" | sed '/ATTACHMENT_DATA:/d')
    
    # Parse attachment data: count|ids|title
    ATTACHMENT_DATA="${ATTACHMENT_SECTION#ATTACHMENT_DATA:}"
    IFS='|' read -r ATTACHMENT_COUNT ATTACHMENT_IDS NOTE_TITLE <<< "$ATTACHMENT_DATA"
    
    # Output main content
    echo "$MAIN_OUTPUT"
    
    # Output attachment info if any
    if [ "$ATTACHMENT_COUNT" -gt 0 ] 2>/dev/null; then
        echo ""
        echo "Attachments: $ATTACHMENT_COUNT file"
        if [ "$ATTACHMENT_COUNT" -gt 1 ]; then
            echo -n "s"
            echo ""
        fi
        
        # Process and output paths
        if [ -n "$ATTACHMENT_IDS" ]; then
            process_attachments "ATTACHMENT_DATA:$ATTACHMENT_IDS" "$NOTE_TITLE"
        fi
    fi
else
    # No attachments
    echo "$RESULT"
fi
