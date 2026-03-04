#!/bin/bash
# Search notes by title then body content, or via Spotlight
# Usage: notes-search.sh <query> [folder] [limit] [--title-only] [--spotlight]
# Folder supports / paths. Use "" for all folders.
# --spotlight uses mdfind to search inside scanned documents (OCR text)

source "$(dirname "$0")/_resolve_folder.sh"

QUERY="" FOLDER="" LIMIT="10" TITLE_ONLY=false SPOTLIGHT=false

for arg in "$@"; do
    case "$arg" in
        --title-only) TITLE_ONLY=true ;;
        --spotlight) SPOTLIGHT=true ;;
        *) 
            if [ -z "$QUERY" ]; then QUERY="$arg"
            elif [ -z "$FOLDER" ]; then FOLDER="$arg"
            else LIMIT="$arg"
            fi ;;
    esac
done

if [ -z "$QUERY" ]; then
    echo "Usage: notes-search.sh <query> [folder] [limit] [--title-only] [--spotlight]"
    exit 1
fi

# Handle spotlight search
if [ "$SPOTLIGHT" = "true" ]; then
    # Search in Notes domain using mdfind (OCR-enabled search)
    if [ -n "$FOLDER" ]; then
        echo "⚠ Spotlight search ignores folder filter (searching all notes)" >&2
    fi
    
    echo "Searching via Spotlight (OCR-enabled)..." >&2
    
    # Use mdfind to search Notes metadata
    # kMDItemContentType = com.apple.notes.note
    results=$(mdfind "kMDItemTextContent == '*$QUERY*' && kMDItemContentType == 'com.apple.notes.note'" 2>/dev/null | head -$LIMIT)
    
    if [ -z "$results" ]; then
        echo "No notes matching '$QUERY' found via Spotlight"
        exit 0
    fi
    
    # Parse results and get note info via AppleScript
    for notePath in $results; do
        # Extract note ID from path or use AppleScript to find it
        noteName=$(basename "$notePath" .note)
        
        # Get note details from Notes app
        osascript <<EOF
tell application "Notes"
    try
        repeat with n in every note
            if name of n contains "$QUERY" then
                set noteId to id of n
                set noteDate to modification date of n
                try
                    set noteFolder to name of container of n
                on error
                    set noteFolder to "?"
                end try
                set y to year of noteDate
                set m to (month of noteDate as integer)
                set d to day of noteDate
                set dateStr to (y as text) & "-" & text -2 thru -1 of ("0" & m) & "-" & text -2 thru -1 of ("0" & d)
                return noteId & " | " & dateStr & " | " & noteFolder & " | " & (name of n)
            end if
        end repeat
    end try
end tell
EOF
    done
    exit 0
fi

# Regular AppleScript search
ESCAPED_QUERY="$(escape_as "$QUERY")"

resolve_folder "$FOLDER"

if [ -z "$FOLDER" ]; then
    echo "⚠ Searching all folders — this may be slow on large collections. Specify a folder for speed." >&2
fi

if [ "$TITLE_ONLY" = "true" ]; then
    BODY_SEARCH="false"
else
    BODY_SEARCH="true"
fi

osascript <<EOF
tell application "Notes"
    try
        $FOLDER_SCRIPT
    on error errMsg
        return "Error: " & errMsg
    end try
    
    set searchTerm to "$ESCAPED_QUERY" as text
    set maxCount to $LIMIT as integer
    set doBodySearch to $BODY_SEARCH as boolean
    set output to ""
    set titleCount to 0
    
    -- Title search (fast)
    repeat with n in noteList
        if titleCount ≥ maxCount then exit repeat
        if name of n contains searchTerm then
            set noteId to id of n
            set noteDate to modification date of n
            try
                set noteFolder to name of container of n
            on error
                set noteFolder to "?"
            end try
            set y to year of noteDate
            set m to (month of noteDate as integer)
            set d to day of noteDate
            set dateStr to (y as text) & "-" & text -2 thru -1 of ("0" & m) & "-" & text -2 thru -1 of ("0" & d)
            set output to output & noteId & " | " & dateStr & " | " & noteFolder & " | " & (name of n) & linefeed
            set titleCount to titleCount + 1
        end if
    end repeat
    
    -- Body search fallback (slower)
    if output is "" and doBodySearch then
        set i to 0
        repeat with n in noteList
            if i ≥ maxCount then exit repeat
            try
                set noteBody to plaintext of n
                if noteBody contains searchTerm then
                    set noteId to id of n
                    set noteDate to modification date of n
                    try
                        set noteFolder to name of container of n
                    on error
                        set noteFolder to "?"
                    end try
                    set y to year of noteDate
                    set m to (month of noteDate as integer)
                    set d to day of noteDate
                    set dateStr to (y as text) & "-" & text -2 thru -1 of ("0" & m) & "-" & text -2 thru -1 of ("0" & d)
                    set output to output & noteId & " | " & dateStr & " | " & noteFolder & " | " & (name of n) & linefeed
                    set i to i + 1
                end if
            end try
        end repeat
    end if
    
    if output is "" then return "No notes matching '" & searchTerm & "' found"
    return output
end tell
EOF
