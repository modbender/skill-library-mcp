#!/bin/bash
# macOS Notes helper via AppleScript
# Usage: notes.sh <command>
#
# Commands:
#   list-folders    List all accounts and folders
#   create-note     Create a note from JSON (reads stdin)
#   read-note       Read a note's content from JSON (reads stdin)
#   list-notes      List notes in a folder from JSON (reads stdin)
#   search-notes    Search notes by title from JSON (reads stdin)

set -euo pipefail

# Verify required dependencies are available
for bin in osascript python3; do
  command -v "$bin" >/dev/null 2>&1 || { echo "Error: $bin is required but not found" >&2; exit 1; }
done

# Ensure Notes.app is running (avoids AppleScript error -600)
# Use -x for exact match to avoid false positives (e.g. "NotesHelper")
if ! pgrep -xq "Notes"; then
  open -a Notes
  sleep 3
fi

LOGFILE="${SKILL_DIR:-$(dirname "$0")/..}/logs/notes.log"

# Append-only action log
log_action() {
  mkdir -p "$(dirname "$LOGFILE")"
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" "$3" >> "$LOGFILE"
}

# Log failures on unexpected exit
trap 'log_action "error" "${cmd:-unknown}" "exit code $?"' ERR

cmd="${1:-help}"

case "$cmd" in
  list-folders)
    osascript <<'APPLESCRIPT'
tell application "Notes"
  set output to ""
  repeat with a in accounts
    repeat with f in folders of a
      set output to output & name of a & " → " & name of f & linefeed
    end repeat
  end repeat
  return output
end tell
APPLESCRIPT
    log_action "list-folders" "-" "-"
    ;;

  create-note)
    json=$(head -c 100000)
    if [ ${#json} -ge 100000 ]; then
        echo "Error: input too large (max 100KB)" >&2
        exit 1
    fi

    validated=$(NOTE_JSON="$json" python3 << 'PYEOF'
import os, sys, json, html as html_module

try:
    data = json.loads(os.environ['NOTE_JSON'])
except json.JSONDecodeError as e:
    print(f"Error: invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)

if 'title' not in data:
    print("Error: 'title' field is required", file=sys.stderr)
    sys.exit(1)

try:
    title = str(data['title'])
    body = str(data.get('body', ''))
    raw_html = str(data.get('html', ''))
    folder = str(data.get('folder', ''))
    account = str(data.get('account', ''))
except (ValueError, TypeError) as e:
    print(f"Error: invalid field value: {e}", file=sys.stderr)
    sys.exit(1)

# Safe output: replace newlines/carriage returns (must be single-line for bash read)
def safe(s):
    return s.replace('\n', ' ').replace('\r', '')

# Field length limits
errors = []
if len(title) > 1000: errors.append("title must be <= 1000 characters")
if len(body) > 99000: errors.append("body must be <= 99000 characters")
if len(raw_html) > 99000: errors.append("html must be <= 99000 characters")
if len(folder) > 255: errors.append("folder must be <= 255 characters")
if len(account) > 255: errors.append("account must be <= 255 characters")
if errors:
    for e in errors:
        print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

# Build HTML body
if raw_html:
    # Sanitize raw_html: strip newlines to prevent multi-line bash read truncation
    safe_html = raw_html.replace('\n', ' ').replace('\r', '')
    note_html = f"<h1>{html_module.escape(title)}</h1>{safe_html}"
elif body:
    # Convert plain text to HTML: escape special chars, convert newlines
    escaped = html_module.escape(body)
    body_html = escaped.replace('\n', '<br>')
    note_html = f"<h1>{html_module.escape(title)}</h1><p>{body_html}</p>"
else:
    note_html = f"<h1>{html_module.escape(title)}</h1>"

print(safe(title))
print(safe(folder) or '-')
print(safe(account) or '-')
print(note_html)
PYEOF
    )

    {
      read -r title
      read -r folder
      read -r account
      # note_html may contain <br> but no real newlines (Python outputs it on one line)
      read -r note_html
    } <<< "$validated"

    # Convert sentinel '-' back to empty string
    [ "$folder" = "-" ] && folder=""
    [ "$account" = "-" ] && account=""

    # Build the AppleScript target dynamically but safely via argv
    result=$(osascript - "$note_html" "$folder" "$account" <<'APPLESCRIPT'
on run argv
    set noteHTML to item 1 of argv
    set folderName to item 2 of argv
    set acctName to item 3 of argv

    tell application "Notes"
        -- Determine target folder
        if acctName is not "" and folderName is not "" then
            set targetFolder to folder folderName of account acctName
        else if folderName is not "" then
            set targetFolder to folder folderName of default account
        else
            set targetFolder to default folder of default account
        end if

        set newNote to make new note at targetFolder with properties {body:noteHTML}
        return "Note created: " & name of newNote
    end tell
end run
APPLESCRIPT
    )
    log_action "create-note" "${account:-default}/${folder:-default}" "$title"
    echo "$result"
    ;;

  read-note)
    json=$(head -c 10000)
    if [ ${#json} -ge 10000 ]; then
        echo "Error: input too large (max 10KB)" >&2
        exit 1
    fi

    validated=$(NOTE_JSON="$json" python3 << 'PYEOF'
import os, sys, json

try:
    data = json.loads(os.environ['NOTE_JSON'])
except json.JSONDecodeError as e:
    print(f"Error: invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)

if 'name' not in data:
    print("Error: 'name' field is required", file=sys.stderr)
    sys.exit(1)

name = str(data['name'])
folder = str(data.get('folder', ''))
account = str(data.get('account', ''))

def safe(s):
    return s.replace('\n', ' ').replace('\r', '')

print(safe(name))
print(safe(folder) or '-')
print(safe(account) or '-')
PYEOF
    )

    {
      read -r name
      read -r folder
      read -r account
    } <<< "$validated"

    [ "$folder" = "-" ] && folder=""
    [ "$account" = "-" ] && account=""

    result=$(osascript - "$name" "$folder" "$account" <<'APPLESCRIPT'
on run argv
    set noteName to item 1 of argv
    set folderName to item 2 of argv
    set acctName to item 3 of argv

    tell application "Notes"
        -- Search in the specified scope
        if acctName is not "" and folderName is not "" then
            set targetNotes to notes of folder folderName of account acctName
        else if acctName is not "" then
            set targetNotes to notes of account acctName
        else if folderName is not "" then
            set targetNotes to notes of folder folderName of default account
        else
            set targetNotes to notes of default account
        end if

        repeat with n in targetNotes
            if name of n is noteName and not password protected of n then
                set noteDate to creation date of n as string
                set noteModDate to modification date of n as string
                return "# " & name of n & linefeed & "Created: " & noteDate & linefeed & "Modified: " & noteModDate & linefeed & linefeed & plaintext of n
            end if
        end repeat

        return "Error: note not found"
    end tell
end run
APPLESCRIPT
    )
    log_action "read-note" "${account:-default}/${folder:-default}" "$name"
    echo "$result"
    ;;

  list-notes)
    json=$(head -c 10000)
    if [ ${#json} -ge 10000 ]; then
        echo "Error: input too large (max 10KB)" >&2
        exit 1
    fi

    validated=$(NOTE_JSON="$json" python3 << 'PYEOF'
import os, sys, json

try:
    data = json.loads(os.environ['NOTE_JSON'])
except json.JSONDecodeError as e:
    print(f"Error: invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)

folder = str(data.get('folder', ''))
account = str(data.get('account', ''))
limit = int(data.get('limit', 20))

if limit < 1 or limit > 200:
    print("Error: limit must be 1-200", file=sys.stderr)
    sys.exit(1)

def safe(s):
    return s.replace('\n', ' ').replace('\r', '')

print(safe(folder) or '-')
print(safe(account) or '-')
print(str(limit))
PYEOF
    )

    {
      read -r folder
      read -r account
      read -r limit
    } <<< "$validated"

    [ "$folder" = "-" ] && folder=""
    [ "$account" = "-" ] && account=""

    # Defense-in-depth: verify limit is a pure integer
    if ! [[ "$limit" =~ ^[0-9]+$ ]]; then
        echo "Error: limit must be an integer" >&2
        exit 1
    fi

    result=$(osascript - "$folder" "$account" "$limit" <<'APPLESCRIPT'
on run argv
    set folderName to item 1 of argv
    set acctName to item 2 of argv
    set noteLimit to (item 3 of argv) as integer

    tell application "Notes"
        -- Determine target
        if acctName is not "" and folderName is not "" then
            set targetNotes to notes of folder folderName of account acctName
        else if acctName is not "" then
            set targetNotes to notes of default folder of account acctName
        else if folderName is not "" then
            set targetNotes to notes of folder folderName of default account
        else
            set targetNotes to notes of default folder of default account
        end if

        set output to ""
        set noteCount to 0
        repeat with n in targetNotes
            if noteCount ≥ noteLimit then exit repeat
            if not password protected of n then
                set noteDate to modification date of n as string
                set isShared to ""
                if shared of n then set isShared to " [shared]"
                set output to output & "- " & name of n & " — " & noteDate & isShared & linefeed
                set noteCount to noteCount + 1
            end if
        end repeat

        if output is "" then
            return "No notes found."
        end if
        return output
    end tell
end run
APPLESCRIPT
    )
    log_action "list-notes" "${account:-default}/${folder:-default}" "-"
    echo "$result"
    ;;

  search-notes)
    json=$(head -c 10000)
    if [ ${#json} -ge 10000 ]; then
        echo "Error: input too large (max 10KB)" >&2
        exit 1
    fi

    validated=$(NOTE_JSON="$json" python3 << 'PYEOF'
import os, sys, json

try:
    data = json.loads(os.environ['NOTE_JSON'])
except json.JSONDecodeError as e:
    print(f"Error: invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)

if 'query' not in data:
    print("Error: 'query' field is required", file=sys.stderr)
    sys.exit(1)

query = str(data['query'])
account = str(data.get('account', ''))
limit = int(data.get('limit', 10))

if limit < 1 or limit > 200:
    print("Error: limit must be 1-200", file=sys.stderr)
    sys.exit(1)
if not query.strip():
    print("Error: query must not be empty", file=sys.stderr)
    sys.exit(1)
if len(query) > 500:
    print("Error: query must be <= 500 characters", file=sys.stderr)
    sys.exit(1)

def safe(s):
    return s.replace('\n', ' ').replace('\r', '')

print(safe(query))
print(safe(account) or '-')
print(str(limit))
PYEOF
    )

    {
      read -r query
      read -r account
      read -r limit
    } <<< "$validated"

    [ "$account" = "-" ] && account=""

    if ! [[ "$limit" =~ ^[0-9]+$ ]]; then
        echo "Error: limit must be an integer" >&2
        exit 1
    fi

    result=$(osascript - "$query" "$account" "$limit" <<'APPLESCRIPT'
on run argv
    set searchQuery to item 1 of argv
    set acctName to item 2 of argv
    set noteLimit to (item 3 of argv) as integer

    tell application "Notes"
        -- Determine target account
        if acctName is not "" then
            set targetAcct to account acctName
        else
            set targetAcct to default account
        end if

        set output to ""
        set matchCount to 0
        -- Search per-folder to reliably access folder name
        repeat with f in folders of targetAcct
            if matchCount ≥ noteLimit then exit repeat
            repeat with n in notes of f
                if matchCount ≥ noteLimit then exit repeat
                if not password protected of n then
                    if name of n contains searchQuery then
                        set noteDate to modification date of n as string
                        set output to output & "- " & name of n & " (" & name of f & ") — " & noteDate & linefeed
                        set matchCount to matchCount + 1
                    end if
                end if
            end repeat
        end repeat

        if output is "" then
            return "No matching notes found"
        end if
        return output
    end tell
end run
APPLESCRIPT
    )
    log_action "search-notes" "${account:-default}" "$query"
    echo "$result"
    ;;

  help|*)
    echo "macOS Notes CLI"
    echo ""
    echo "Commands:"
    echo "  list-folders    List all accounts and folders"
    echo "  create-note     Create a note from JSON (reads stdin)"
    echo "  read-note       Read a note by name from JSON (reads stdin)"
    echo "  list-notes      List notes in a folder from JSON (reads stdin)"
    echo "  search-notes    Search notes by title from JSON (reads stdin)"
    echo ""
    echo "Usage:"
    echo "  echo '<json>' | notes.sh create-note"
    echo ""
    echo "JSON fields (create-note):"
    echo "  title        (required) Note title"
    echo "  body         Plain text content (newlines become <br>)"
    echo "  html         Raw HTML content (overrides body)"
    echo "  folder       Folder name (auto-detects if omitted)"
    echo "  account      Account name (auto-detects if omitted)"
    ;;
esac
