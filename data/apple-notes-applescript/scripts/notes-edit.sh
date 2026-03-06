#!/bin/bash
# Replace a note's body
# Usage: notes-edit.sh <note-name-or-id> <new-body> [folder]
# If name starts with "x-coredata" it's treated as ID lookup

source "$(dirname "$0")/_resolve_folder.sh"

NAME="${1:-}"
BODY="${2:-}"
FOLDER="${3:-}"

if [ -z "$NAME" ] || [ -z "$BODY" ]; then
    echo "Usage: notes-edit.sh <note-name-or-id> <new-body> [folder]"
    exit 1
fi

ESCAPED_NAME="$(escape_as "$NAME")"

TMPFILE=$(mktemp /tmp/notes-edit.XXXXXX)
printf '%s' "$BODY" > "$TMPFILE"
trap "rm -f '$TMPFILE'" EXIT

# ID lookup — direct
if [[ "$NAME" == x-coredata* ]]; then
    osascript <<EOF
set bodyFile to POSIX file "$TMPFILE"
set bodyText to read bodyFile as «class utf8»

tell application "Notes"
    try
        set n to note id "$ESCAPED_NAME"
        set noteTitle to name of n
        set body of n to "<h1>" & noteTitle & "</h1><br>" & bodyText
        return "Updated: " & noteTitle
    on error errMsg
        return "Error: " & errMsg
    end try
end tell
EOF
    exit $?
fi

# Name lookup
resolve_folder "$FOLDER"

osascript <<EOF
set bodyFile to POSIX file "$TMPFILE"
set bodyText to read bodyFile as «class utf8»

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
            set body of n to "<h1>" & noteTitle & "</h1><br>" & bodyText
            return "Updated: " & noteTitle
        end if
    end repeat
    return "Error: No note matching '" & searchTerm & "' found"
end tell
EOF
