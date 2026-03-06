#!/bin/bash
# Shared folder resolution helper
# Splits on "/" only when NOT surrounded by spaces (path separator vs folder name)
# Usage: source this, then call resolve_folder "$FOLDER"
# Sets FOLDER_SCRIPT variable

escape_as() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

resolve_folder() {
    local folder="$1"
    if [ -z "$folder" ]; then
        FOLDER_SCRIPT="set noteList to every note"
        return
    fi
    
    # Split on "/" but only when not surrounded by spaces
    # "Scanned/Finance / Tax" → ["Scanned", "Finance / Tax"]
    # "Scanned/Medical & Health" → ["Scanned", "Medical & Health"]
    local parts=()
    local current=""
    local len=${#folder}
    local i=0
    
    while [ $i -lt $len ]; do
        local char="${folder:$i:1}"
        if [ "$char" = "/" ]; then
            # Check if surrounded by spaces (part of folder name) or path separator
            local prev_char=""
            local next_char=""
            [ $i -gt 0 ] && prev_char="${folder:$((i-1)):1}"
            [ $i -lt $((len-1)) ] && next_char="${folder:$((i+1)):1}"
            
            if [ "$prev_char" = " " ] || [ "$next_char" = " " ]; then
                # Part of folder name (e.g. "Finance / Tax")
                current="${current}${char}"
            else
                # Path separator
                parts+=("$current")
                current=""
            fi
        else
            current="${current}${char}"
        fi
        i=$((i+1))
    done
    [ -n "$current" ] && parts+=("$current")
    
    FOLDER_SCRIPT="set targetFolder to folder \"$(escape_as "${parts[0]}")\""
    for ((i=1; i<${#parts[@]}; i++)); do
        FOLDER_SCRIPT="$FOLDER_SCRIPT
        set targetFolder to folder \"$(escape_as "${parts[$i]}")\" of targetFolder"
    done
    FOLDER_SCRIPT="$FOLDER_SCRIPT
        set noteList to notes of targetFolder"
}
