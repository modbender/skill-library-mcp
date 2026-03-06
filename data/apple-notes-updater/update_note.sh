#!/bin/bash

NOTE_TITLE="$1"
NEW_BODY="$2"

# Создаем временный файл для NEW_BODY
TMP_FILE=$(mktemp)
echo "$NEW_BODY" > "$TMP_FILE"

osascript <<EOF
set noteTitle to "$NOTE_TITLE"
set newBodyFilePath to (POSIX file "$TMP_FILE") as alias

tell application "Notes"
    set theNote to first note whose name is noteTitle
    
    set fileRef to open for access newBodyFilePath
    set theContent to read fileRef as «class utf8»
    close access fileRef
    
    set body of theNote to theContent
end tell
return "Note '" & noteTitle & "' updated with content."
EOF

# Удаляем временный файл
rm "$TMP_FILE"