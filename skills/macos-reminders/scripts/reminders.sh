#!/bin/bash
# macOS Reminders helper via AppleScript
# Usage: reminders.sh <command>
#
# Commands:
#   list-lists                  List all available reminder lists
#   create-reminder             Create a reminder from JSON (reads stdin)
#   list-reminders              List reminders from JSON filter (reads stdin)

set -euo pipefail

# Verify required dependencies are available
for bin in osascript python3; do
  command -v "$bin" >/dev/null 2>&1 || { echo "Error: $bin is required but not found" >&2; exit 1; }
done

# Ensure Reminders.app is running (avoids AppleScript error -600)
if ! pgrep -q "Reminders"; then
  open -a Reminders
  sleep 2
fi

LOGFILE="${SKILL_DIR:-$(dirname "$0")/..}/logs/reminders.log"

# Append-only action log
log_action() {
  mkdir -p "$(dirname "$LOGFILE")"
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" "$3" >> "$LOGFILE"
}

# Log failures on unexpected exit (non-zero, non-help)
trap 'log_action "error" "${cmd:-unknown}" "exit code $?"' ERR

cmd="${1:-help}"

case "$cmd" in
  list-lists)
    osascript -e 'tell application "Reminders"
      set output to ""
      repeat with l in lists
        set output to output & name of l & linefeed
      end repeat
      return output
    end tell'
    log_action "list-lists" "-" "-"
    ;;

  create-reminder)
    # Read JSON from stdin (avoids exposing sensitive data in process list)
    json=$(head -c 10000)
    if [ ${#json} -ge 10000 ]; then
        echo "Error: input too large (max 10KB)" >&2
        exit 1
    fi

    # Validate, normalize, and extract all fields in a single Python call.
    # Outputs one field per line for safe bash parsing.
    # JSON is passed via environment variable (not pipe) because the heredoc
    # already occupies stdin.
    validated=$(REMINDER_JSON="$json" python3 << 'PYEOF'
import os, sys, json

try:
    data = json.loads(os.environ['REMINDER_JSON'])
except json.JSONDecodeError as e:
    print(f"Error: invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)

if 'name' not in data:
    print("Error: 'name' field is required", file=sys.stderr)
    sys.exit(1)

try:
    name = str(data['name'])
    list_name = str(data.get('list', ''))
    body = str(data.get('body', ''))
    iso_date = str(data.get('iso_date', ''))
    offset_days = data.get('offset_days', '')
    hour = int(data.get('hour', 9))
    minute = int(data.get('minute', 0))
    priority = int(data.get('priority', 0))
    flagged = bool(data.get('flagged', False))
except (ValueError, TypeError) as e:
    print(f"Error: invalid field value: {e}", file=sys.stderr)
    sys.exit(1)

# Determine if a due date was requested
has_due_date = False
if iso_date or offset_days != '':
    has_due_date = True
    if offset_days != '':
        try:
            offset_days = int(offset_days)
        except (ValueError, TypeError):
            print("Error: offset_days must be an integer", file=sys.stderr)
            sys.exit(1)
    else:
        offset_days = 0

# Range checks
errors = []
if not 0 <= hour <= 23: errors.append("hour must be 0-23")
if not 0 <= minute <= 59: errors.append("minute must be 0-59")
if priority not in (0, 1, 5, 9): errors.append("priority must be 0 (none), 1 (high), 5 (medium), or 9 (low)")

# Validate and normalize iso_date (ensure zero-padded YYYY-MM-DD)
if iso_date:
    parts = iso_date.split('-')
    if len(parts) != 3:
        errors.append("iso_date must be YYYY-MM-DD")
    else:
        try:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            if not (1 <= m <= 12 and 1 <= d <= 31 and y >= 1):
                errors.append("iso_date has invalid date values")
            else:
                iso_date = f"{y:04d}-{m:02d}-{d:02d}"
        except ValueError:
            errors.append("iso_date must contain numeric values")

if errors:
    for e in errors:
        print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

# Safe output: replace newlines in string values
def safe(s):
    return s.replace('\n', ' ').replace('\r', '')

fields = [
    safe(name), safe(list_name), safe(body), safe(iso_date),
    str(offset_days) if has_due_date else '',
    str(hour), str(minute), str(priority),
    'true' if flagged else 'false',
    'true' if has_due_date else 'false'
]
for f in fields:
    print(f)
PYEOF
    )

    # Read validated values (one field per line)
    {
      read -r name
      read -r list_name
      read -r body
      read -r iso_date
      read -r offset_days
      read -r hour
      read -r minute
      read -r priority
      read -r flagged
      read -r has_due_date
    } <<< "$validated"

    # Defense-in-depth: verify numeric fields are pure integers
    for var in hour minute priority; do
        if ! [[ "${!var}" =~ ^-?[0-9]+$ ]]; then
            echo "Error: $var must be an integer" >&2
            exit 1
        fi
    done
    if [ -n "$offset_days" ]; then
        if ! [[ "$offset_days" =~ ^-?[0-9]+$ ]]; then
            echo "Error: offset_days must be an integer" >&2
            exit 1
        fi
    fi

    # Auto-detect list if not specified
    if [ -z "$list_name" ]; then
        list_name=$(osascript -e 'tell application "Reminders" to get name of default list')
    fi

    # Verify the target list exists before attempting to create
    if ! osascript - "$list_name" <<'CHECKSCRIPT' >/dev/null 2>&1; then
on run argv
    tell application "Reminders" to get list (item 1 of argv)
end run
CHECKSCRIPT
        echo "Error: reminder list '$list_name' not found. Run list-lists to see available lists." >&2
        exit 1
    fi

    # Execute via osascript with argv parameter passing.
    # All user-provided strings are passed as typed parameters via "on run argv",
    # never interpolated into executable AppleScript code. This prevents injection.
    result=$(osascript - "$name" "$body" "$list_name" \
        "$offset_days" "$hour" "$minute" "$priority" \
        "$flagged" "$has_due_date" "$iso_date" <<'APPLESCRIPT'
on run argv
    set remName to item 1 of argv
    set remBody to item 2 of argv
    set listName to item 3 of argv
    set offsetDays to item 4 of argv
    set remHour to (item 5 of argv) as integer
    set remMinute to (item 6 of argv) as integer
    set remPriority to (item 7 of argv) as integer
    set isFlagged to (item 8 of argv) is "true"
    set hasDueDate to (item 9 of argv) is "true"
    set isoDate to item 10 of argv

    -- Calculate due date if requested
    set dueDate to missing value
    if hasDueDate then
        if isoDate is not "" then
            set dueDate to current date
            set year of dueDate to (text 1 thru 4 of isoDate) as integer
            set month of dueDate to (text 6 thru 7 of isoDate) as integer
            set day of dueDate to (text 9 thru 10 of isoDate) as integer
            set hours of dueDate to remHour
            set minutes of dueDate to remMinute
            set seconds of dueDate to 0
        else
            set dueDate to (current date) + (offsetDays as integer) * days
            set hours of dueDate to remHour
            set minutes of dueDate to remMinute
            set seconds of dueDate to 0
        end if
    end if

    -- Create reminder then set properties individually
    -- (AppleScript record concatenation does not work with app-defined property names)
    tell application "Reminders"
        tell list listName
            set newReminder to make new reminder with properties {name:remName, body:remBody}
            set priority of newReminder to remPriority
            set flagged of newReminder to isFlagged
            if dueDate is not missing value then
                set due date of newReminder to dueDate
                set remind me date of newReminder to dueDate
            end if
        end tell
    end tell

    if hasDueDate then
        return "Reminder created: " & remName & " (due " & (dueDate as string) & ")"
    else
        return "Reminder created: " & remName
    end if
end run
APPLESCRIPT
    )
    log_action "create-reminder" "$list_name" "$name"
    echo "$result"
    ;;

  list-reminders)
    # Read JSON filter from stdin
    json=$(head -c 10000)
    if [ ${#json} -ge 10000 ]; then
        echo "Error: input too large (max 10KB)" >&2
        exit 1
    fi

    # Parse filter options
    filter=$(REMINDER_JSON="$json" python3 << 'PYEOF'
import os, sys, json

try:
    data = json.loads(os.environ['REMINDER_JSON'])
except json.JSONDecodeError as e:
    print(f"Error: invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)

list_name = str(data.get('list', ''))
include_completed = bool(data.get('include_completed', False))

def safe(s):
    return s.replace('\n', ' ').replace('\r', '')

print(safe(list_name))
print('true' if include_completed else 'false')
PYEOF
    )

    {
      read -r list_name
      read -r include_completed
    } <<< "$filter"

    result=$(osascript - "$list_name" "$include_completed" <<'APPLESCRIPT'
on run argv
    set filterList to item 1 of argv
    set includeCompleted to (item 2 of argv) is "true"

    tell application "Reminders"
        set output to ""
        if filterList is not "" then
            set targetLists to {list filterList}
        else
            set targetLists to lists
        end if

        repeat with l in targetLists
            set output to output & "## " & name of l & linefeed
            set rems to reminders of l
            repeat with r in rems
                if includeCompleted or not completed of r then
                    set line_text to ""
                    if completed of r then
                        set line_text to line_text & "[x] "
                    else
                        set line_text to line_text & "[ ] "
                    end if
                    set line_text to line_text & name of r
                    if priority of r > 0 then
                        if priority of r = 1 then
                            set line_text to line_text & " !!!"
                        else if priority of r = 5 then
                            set line_text to line_text & " !!"
                        else if priority of r = 9 then
                            set line_text to line_text & " !"
                        end if
                    end if
                    if flagged of r then
                        set line_text to line_text & " [flagged]"
                    end if
                    if due date of r is not missing value then
                        set line_text to line_text & " — due " & (due date of r as string)
                    end if
                    set output to output & line_text & linefeed
                end if
            end repeat
            set output to output & linefeed
        end repeat
        return output
    end tell
end run
APPLESCRIPT
    )
    log_action "list-reminders" "${list_name:--}" "-"
    echo "$result"
    ;;

  help|*)
    echo "macOS Reminders CLI"
    echo ""
    echo "Commands:"
    echo "  list-lists                  List all reminder lists"
    echo "  create-reminder             Create reminder from JSON (reads stdin)"
    echo "  list-reminders              List reminders from JSON filter (reads stdin)"
    echo ""
    echo "Usage:"
    echo "  echo '<json>' | reminders.sh create-reminder"
    echo ""
    echo "JSON fields (create-reminder):"
    echo "  name           (required) Reminder title"
    echo "  list           Reminder list name (auto-detects if omitted)"
    echo "  body           Notes/details"
    echo "  offset_days    Due date as days from today (0=today, 1=tomorrow)"
    echo "  iso_date       Absolute due date YYYY-MM-DD (overrides offset_days)"
    echo "  hour           Due time hour 0-23 (default: 9)"
    echo "  minute         Due time minute 0-59 (default: 0)"
    echo "  priority       0=none, 1=high, 5=medium, 9=low (default: 0)"
    echo "  flagged        true/false (default: false)"
    ;;
esac
