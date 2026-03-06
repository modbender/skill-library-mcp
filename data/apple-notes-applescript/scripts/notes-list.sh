#!/bin/bash
# List notes (ID | Date | Title)
# Usage: notes-list.sh [folder] [limit]
# Folder supports / paths: "Scanned/Medical & Health"
# Without folder, defaults to limit 20 with warning

source "$(dirname "$0")/_resolve_folder.sh"

FOLDER="${1:-}"
LIMIT="${2:-20}"

resolve_folder "$FOLDER"

if [ -z "$FOLDER" ]; then
    echo "⚠ No folder specified — listing up to $LIMIT notes from all folders (may be slow on large collections)" >&2
    SHOW_FOLDER="true"
else
    SHOW_FOLDER="false"
fi

osascript <<EOF
tell application "Notes"
    try
        $FOLDER_SCRIPT
    on error errMsg
        return "Error: " & errMsg
    end try
    
    set maxCount to $LIMIT as integer
    set showFolder to $SHOW_FOLDER as boolean
    set output to ""
    set i to 0
    repeat with n in noteList
        if i ≥ maxCount then exit repeat
        set noteId to id of n
        set noteDate to modification date of n
        set noteTitle to name of n
        set y to year of noteDate
        set m to (month of noteDate as integer)
        set d to day of noteDate
        set dateStr to (y as text) & "-" & text -2 thru -1 of ("0" & m) & "-" & text -2 thru -1 of ("0" & d)
        if showFolder then
            try
                set fName to name of container of n
            on error
                set fName to "?"
            end try
            set output to output & noteId & " | " & dateStr & " | " & fName & " | " & noteTitle & linefeed
        else
            set output to output & noteId & " | " & dateStr & " | " & noteTitle & linefeed
        end if
        set i to i + 1
    end repeat
    if output is "" then return "No notes found"
    return output
end tell
EOF
