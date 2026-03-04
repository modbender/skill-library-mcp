#!/bin/bash
# macOS Calendar helper via AppleScript
# Usage: calendar.sh <command>
#
# Commands:
#   list-calendars              List all available calendars
#   create-event                Create an event from JSON (reads stdin)

set -euo pipefail

# Verify required dependencies are available
for bin in osascript python3; do
  command -v "$bin" >/dev/null 2>&1 || { echo "Error: $bin is required but not found" >&2; exit 1; }
done

# Ensure Calendar.app is running (avoids AppleScript error -600)
if ! pgrep -q "Calendar"; then
  open -a Calendar
  sleep 2
fi

LOGFILE="${SKILL_DIR:-$(dirname "$0")/..}/logs/calendar.log"

# SR-004: Append-only action log
log_action() {
  mkdir -p "$(dirname "$LOGFILE")"
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" "$3" >> "$LOGFILE"
}

cmd="${1:-help}"

case "$cmd" in
  list-calendars)
    osascript -e 'tell application "Calendar"
      set output to ""
      repeat with c in calendars
        if writable of c then
          set output to output & name of c & linefeed
        else
          set output to output & name of c & " [read-only]" & linefeed
        end if
      end repeat
      return output
    end tell'
    log_action "list-calendars" "-" "-"
    ;;

  create-event)
    # Read JSON from stdin (avoids exposing sensitive data in process list)
    json=$(cat)

    # Validate, normalize, and extract all fields in a single Python call.
    # Outputs tab-separated values on one line.
    # Tabs and newlines in string values are replaced with spaces for safe parsing.
    # JSON is passed via environment variable (not pipe) because the heredoc
    # already occupies stdin — a pipe would be silently discarded by bash.
    validated=$(CALENDAR_JSON="$json" python3 << 'PYEOF'
import os, sys, json

try:
    data = json.loads(os.environ['CALENDAR_JSON'])
except json.JSONDecodeError as e:
    print(f"Error: invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)

if 'summary' not in data:
    print("Error: 'summary' field is required", file=sys.stderr)
    sys.exit(1)

try:
    summary = str(data['summary'])
    calendar = str(data.get('calendar', ''))
    description = str(data.get('description', ''))
    recurrence = str(data.get('recurrence', ''))
    iso_date = str(data.get('iso_date', ''))
    offset_days = int(data.get('offset_days', 0))
    hour = int(data.get('hour', 9))
    minute = int(data.get('minute', 0))
    duration_min = int(data.get('duration_minutes', 30))
    alarm_min = int(data.get('alarm_minutes', 0))
    all_day = bool(data.get('all_day', False))
except (ValueError, TypeError) as e:
    print(f"Error: invalid field value: {e}", file=sys.stderr)
    sys.exit(1)

# Range checks
errors = []
if not 0 <= hour <= 23: errors.append("hour must be 0-23")
if not 0 <= minute <= 59: errors.append("minute must be 0-59")
if duration_min < 0: errors.append("duration_minutes must be >= 0")
if alarm_min < 0: errors.append("alarm_minutes must be >= 0")

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

# Safe output: replace newlines in string values (one field per line)
def safe(s):
    return s.replace('\n', ' ').replace('\r', '')

fields = [
    safe(summary), safe(calendar), safe(description), safe(recurrence), safe(iso_date),
    str(offset_days), str(hour), str(minute), str(duration_min), str(alarm_min),
    'true' if all_day else 'false'
]
for f in fields:
    print(f)
PYEOF
    )

    # Read validated values (one field per line, handles empty fields correctly)
    {
      read -r summary
      read -r calendar
      read -r description
      read -r recurrence
      read -r iso_date
      read -r offset_days
      read -r hour
      read -r minute
      read -r duration_min
      read -r alarm_min
      read -r all_day
    } <<< "$validated"

    # Defense-in-depth: verify numeric fields are pure integers
    for var in offset_days hour minute duration_min alarm_min; do
        if ! [[ "${!var}" =~ ^-?[0-9]+$ ]]; then
            echo "Error: $var must be an integer" >&2
            exit 1
        fi
    done

    # Auto-detect calendar if not specified
    if [ -z "$calendar" ]; then
        calendar=$(osascript -e 'tell application "Calendar" to get name of first calendar')
    fi

    # Execute via osascript with argv parameter passing.
    # All user-provided strings are passed as typed parameters via "on run argv",
    # never interpolated into executable AppleScript code. This prevents injection.
    result=$(osascript - "$summary" "$description" "$calendar" "$recurrence" \
        "$offset_days" "$hour" "$minute" "$duration_min" "$alarm_min" \
        "$all_day" "$iso_date" <<'APPLESCRIPT'
on run argv
    set evtSummary to item 1 of argv
    set evtDescription to item 2 of argv
    set calName to item 3 of argv
    set evtRecurrence to item 4 of argv
    set offsetDays to (item 5 of argv) as integer
    set evtHour to (item 6 of argv) as integer
    set evtMinute to (item 7 of argv) as integer
    set durationMin to (item 8 of argv) as integer
    set alarmMin to (item 9 of argv) as integer
    set isAllDay to (item 10 of argv) is "true"
    set isoDate to item 11 of argv

    -- Calculate start date
    if isoDate is not "" then
        set startDate to current date
        set year of startDate to (text 1 thru 4 of isoDate) as integer
        set month of startDate to (text 6 thru 7 of isoDate) as integer
        set day of startDate to (text 9 thru 10 of isoDate) as integer
        set hours of startDate to evtHour
        set minutes of startDate to evtMinute
        set seconds of startDate to 0
    else
        set startDate to (current date) + offsetDays * days
        set hours of startDate to evtHour
        set minutes of startDate to evtMinute
        set seconds of startDate to 0
    end if

    -- Create event
    tell application "Calendar"
        -- SR-001: Reject read-only calendars
        if not (writable of calendar calName) then
            error "Calendar '" & calName & "' is read-only. Choose a writable calendar."
        end if
        tell calendar calName
            if isAllDay then
                set newEvent to make new event with properties {summary:evtSummary, start date:startDate, end date:startDate, allday event:true, description:evtDescription}
            else
                set endDate to startDate + durationMin * minutes
                set newEvent to make new event with properties {summary:evtSummary, start date:startDate, end date:endDate, description:evtDescription}
            end if

            -- Set recurrence if provided
            if evtRecurrence is not "" then
                set recurrence of newEvent to evtRecurrence
            end if

            -- Set alarm if provided
            if alarmMin > 0 then
                make new display alarm at end of newEvent with properties {trigger interval:-alarmMin}
            end if
        end tell
    end tell

    return "Event created: " & evtSummary
end run
APPLESCRIPT
    )
    log_action "create-event" "$calendar" "$summary"
    echo "$result"
    ;;

  help|*)
    echo "macOS Calendar CLI"
    echo ""
    echo "Commands:"
    echo "  list-calendars              List all calendars"
    echo "  create-event                Create event from JSON (reads stdin)"
    echo ""
    echo "Usage:"
    echo "  echo '<json>' | calendar.sh create-event"
    echo ""
    echo "JSON fields:"
    echo "  summary        (required) Event title"
    echo "  calendar       Calendar name (auto-detects if omitted)"
    echo "  description    Event notes"
    echo "  offset_days    Days from today (default: 0)"
    echo "  iso_date       Absolute date YYYY-MM-DD (overrides offset_days)"
    echo "  hour           Start hour 0-23 (default: 9)"
    echo "  minute         Start minute 0-59 (default: 0)"
    echo "  duration_minutes  Duration in minutes (default: 30)"
    echo "  alarm_minutes  Alert before event in minutes (0=none)"
    echo "  all_day        true/false (default: false)"
    echo "  recurrence     iCal RRULE (e.g. FREQ=WEEKLY;BYDAY=TU)"
    ;;
esac
