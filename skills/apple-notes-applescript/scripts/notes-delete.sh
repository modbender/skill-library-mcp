#!/bin/bash
# Delete a note by name (partial match)
# Usage: notes-delete.sh <note-name> <folder>
# Folder is REQUIRED for safety (avoids searching 4000+ notes)

source "$(dirname "$0")/_resolve_folder.sh"

NAME="${1:-}"
FOLDER="${2:-}"

if [ -z "$NAME" ] || [ -z "$FOLDER" ]; then
    echo "Usage: notes-delete.sh <note-name> <folder>"
    echo "Folder is required for safety."
    exit 1
fi

ESCAPED_NAME="$(escape_as "$NAME")"

resolve_folder "$FOLDER"

osascript <<EOF
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
            try
                set noteFolder to name of container of n
            on error
                set noteFolder to "unknown"
            end try
            delete n
            return "Deleted: " & noteTitle & " (from " & noteFolder & ")"
        end if
    end repeat
    return "Error: No note matching '" & searchTerm & "' found in $FOLDER"
end tell
EOF
