#!/bin/bash
# List all Notes folders
# Usage: notes-folders.sh [--tree] [--counts]

show_tree=false
show_counts=false
for arg in "$@"; do
    case "$arg" in
        --tree) show_tree=true ;;
        --counts) show_counts=true ;;
    esac
done

if [ "$show_tree" = "true" ]; then
    osascript <<'EOF'
on listFolders(parentFolder, indent)
    set output to ""
    tell application "Notes"
        set subfolders to every folder of parentFolder
        repeat with f in subfolders
            set fname to name of f
            set c to number of notes of f
            set output to output & indent & fname & " (" & c & ")" & linefeed
        end repeat
    end tell
    repeat with f in subfolders
        set output to output & my listFolders(f, indent & "  ")
    end repeat
    return output
end listFolders

tell application "Notes"
    set output to ""
    repeat with acct in every account
        set acctName to name of acct
        set output to output & "[" & acctName & "]" & linefeed
        set topFolders to every folder of acct
        repeat with f in topFolders
            set fname to name of f
            set c to number of notes of f
            set output to output & "  " & fname & " (" & c & ")" & linefeed
            set output to output & my listFolders(f, "    ")
        end repeat
    end repeat
    return output
end tell
EOF
elif [ "$show_counts" = "true" ]; then
    osascript <<'EOF'
tell application "Notes"
    set output to ""
    repeat with f in every folder
        set fname to name of f
        set c to number of notes of f
        set output to output & fname & " (" & c & ")" & linefeed
    end repeat
    return output
end tell
EOF
else
    osascript -e 'tell application "Notes" to get name of every folder' | tr ',' '\n' | sed 's/^ //'
fi
