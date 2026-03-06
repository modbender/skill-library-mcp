#!/bin/bash
# Create a new note
# Usage: notes-create.sh <folder> <title> [body]
# Folder supports / paths. Body is optional (empty note with just title).

source "$(dirname "$0")/_resolve_folder.sh"

FOLDER="${1:-}"
TITLE="${2:-}"
BODY="${3:-}"

if [ -z "$FOLDER" ] || [ -z "$TITLE" ]; then
    echo "Usage: notes-create.sh <folder> <title> [body]"
    exit 1
fi

resolve_folder "$FOLDER"

# For create, we don't need "set noteList to notes of targetFolder"
# Remove the last line from FOLDER_SCRIPT
FOLDER_SCRIPT="${FOLDER_SCRIPT%
        set noteList to notes of targetFolder}"

ESCAPED_TITLE="$(escape_as "$TITLE")"

TMPFILE=$(mktemp /tmp/notes-create.XXXXXX)
printf '%s' "$BODY" > "$TMPFILE"
trap "rm -f '$TMPFILE'" EXIT

osascript <<EOF
set bodyFile to POSIX file "$TMPFILE"
set bodyText to read bodyFile as «class utf8»

tell application "Notes"
    try
        $FOLDER_SCRIPT
    on error errMsg
        return "Error: " & errMsg
    end try
    
    if bodyText is "" then
        set htmlBody to "<h1>$ESCAPED_TITLE</h1>"
    else
        set htmlBody to "<h1>$ESCAPED_TITLE</h1><br>" & bodyText
    end if
    set newNote to make new note at targetFolder with properties {name:"$ESCAPED_TITLE", body:htmlBody}
    set newId to id of newNote
    return "Created: $ESCAPED_TITLE" & linefeed & "Folder: $FOLDER" & linefeed & "ID: " & newId
end tell
EOF
