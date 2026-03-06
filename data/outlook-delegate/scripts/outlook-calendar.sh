#!/bin/bash
# Outlook Calendar Operations - Delegate Version
# Usage: outlook-calendar.sh <command> [args]
#
# Accesses the owner's calendar as a delegate.
# All times are handled in the configured timezone.

CONFIG_DIR="$HOME/.outlook-mcp"
CREDS_FILE="$CONFIG_DIR/credentials.json"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Load token
ACCESS_TOKEN=$(jq -r '.access_token' "$CREDS_FILE" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
    echo '{"error": "No access token. Run outlook-token.sh refresh or complete setup."}'
    exit 1
fi

# Write auth header to a secure temp file so the token doesn't appear
# in the process list (visible via /proc/[pid]/cmdline on Linux).
AUTH_HEADER_FILE=$(mktemp)
chmod 600 "$AUTH_HEADER_FILE"
printf 'header "Authorization: Bearer %s"' "$ACCESS_TOKEN" > "$AUTH_HEADER_FILE"
trap 'rm -f "$AUTH_HEADER_FILE"' EXIT

# Load config
OWNER_EMAIL=$(jq -r '.owner_email' "$CONFIG_FILE" 2>/dev/null)
TIMEZONE=$(jq -r '.timezone // "UTC"' "$CONFIG_FILE" 2>/dev/null)

if [ -z "$OWNER_EMAIL" ] || [ "$OWNER_EMAIL" = "null" ]; then
    echo '{"error": "No owner_email in config.json"}'
    exit 1
fi

# API base URL for owner's calendar
API="https://graph.microsoft.com/v1.0/users/$OWNER_EMAIL"

# Helper: find full event ID from partial suffix
find_full_event_id() {
    local PARTIAL_ID="$1"
    curl -s "$API/calendar/events?\$top=200&\$select=id&\$orderby=start/dateTime%20desc" \
        -K "$AUTH_HEADER_FILE" | \
        jq -r --arg suffix "$PARTIAL_ID" '.value[] | select(.id | endswith($suffix)) | .id' | head -1
}

# Helper: get timezone-aware date boundaries
# IMPORTANT: calendarView startDateTime/endDateTime are parsed using the offset
# in the value itself, NOT the Prefer: outlook.timezone header. We must include
# the UTC offset so Graph interprets the times correctly.
get_utc_offset() {
    # Returns offset like +05:00 or -04:00
    TZ="$TIMEZONE" date +"%z" | sed 's/\([+-][0-9][0-9]\)\([0-9][0-9]\)/\1:\2/'
}

get_now() {
    local OFFSET
    OFFSET=$(get_utc_offset)
    TZ="$TIMEZONE" date +"%Y-%m-%dT%H:%M:%S${OFFSET}"
}

get_today_start() {
    local OFFSET
    OFFSET=$(get_utc_offset)
    TZ="$TIMEZONE" date +"%Y-%m-%dT00:00:00${OFFSET}"
}

get_today_end() {
    local OFFSET
    OFFSET=$(get_utc_offset)
    TZ="$TIMEZONE" date +"%Y-%m-%dT23:59:59${OFFSET}"
}

get_week_end() {
    # 7 days from now in configured timezone
    local OFFSET
    OFFSET=$(get_utc_offset)
    TZ="$TIMEZONE" date -d "+7 days" +"%Y-%m-%dT23:59:59${OFFSET}" 2>/dev/null || \
    TZ="$TIMEZONE" date -v+7d +"%Y-%m-%dT23:59:59${OFFSET}" 2>/dev/null || \
    date -u -d "+7 days" +"%Y-%m-%dT23:59:59+00:00"
}

case "$1" in
    events)
        # List owner's upcoming events (future only)
        COUNT=${2:-10}
        COUNT=$(echo "$COUNT" | grep -o '^[0-9]*' | head -1)
        COUNT=${COUNT:-10}
        NOW=$(get_now)
        curl -s "$API/calendarView?startDateTime=$NOW&endDateTime=2099-12-31T23:59:59Z&\$top=$COUNT&\$orderby=start/dateTime&\$select=id,subject,start,end,location,isAllDay" \
            -K "$AUTH_HEADER_FILE" \
            -H "Prefer: outlook.timezone=\"$TIMEZONE\"" | jq 'if .error then {error: .error.message} else (.value | to_entries | .[] | {n: (.key + 1), subject: .value.subject, start: .value.start.dateTime[0:16], end: .value.end.dateTime[0:16], location: (.value.location.displayName // ""), id: .value.id[-20:]}) end'
        ;;
    
    today)
        # List today's events (timezone-aware)
        TODAY_START=$(get_today_start)
        TODAY_END=$(get_today_end)
        
        curl -s "$API/calendarView?startDateTime=$TODAY_START&endDateTime=$TODAY_END&\$orderby=start/dateTime&\$select=id,subject,start,end,location" \
            -K "$AUTH_HEADER_FILE" \
            -H "Prefer: outlook.timezone=\"$TIMEZONE\"" | jq 'if .error then {error: .error.message} else (if .value then (if (.value | length) == 0 then {info: "No events today", timezone: "'"$TIMEZONE"'"} else (.value | to_entries | .[] | {n: (.key + 1), subject: .value.subject, start: .value.start.dateTime[0:16], end: .value.end.dateTime[0:16], location: (.value.location.displayName // ""), id: .value.id[-20:]}) end) else {info: "No events today"} end) end'
        ;;
    
    week)
        # List this week's events (timezone-aware)
        WEEK_START=$(get_today_start)
        WEEK_END=$(get_week_end)
        
        curl -s "$API/calendarView?startDateTime=$WEEK_START&endDateTime=$WEEK_END&\$orderby=start/dateTime&\$select=id,subject,start,end,location,isAllDay" \
            -K "$AUTH_HEADER_FILE" \
            -H "Prefer: outlook.timezone=\"$TIMEZONE\"" | jq 'if .error then {error: .error.message} else (if .value then (if (.value | length) == 0 then {info: "No events this week", timezone: "'"$TIMEZONE"'"} else (.value | to_entries | .[] | {n: (.key + 1), subject: .value.subject, start: .value.start.dateTime[0:16], end: .value.end.dateTime[0:16], location: (.value.location.displayName // ""), id: .value.id[-20:]}) end) else {info: "No events this week"} end) end'
        ;;
    
    read)
        # Read event details
        EVENT_ID="$2"
        FULL_ID=$(find_full_event_id "$EVENT_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Event not found"}'
            exit 1
        fi
        
        curl -s "$API/calendar/events/$FULL_ID" \
            -K "$AUTH_HEADER_FILE" \
            -H "Prefer: outlook.timezone=\"$TIMEZONE\"" | jq 'if .error then {error: .error.message} else {
                subject,
                start: .start.dateTime,
                end: .end.dateTime,
                timezone: .start.timeZone,
                location: .location.displayName,
                body: (if .body.contentType == "html" then (.body.content | gsub("<[^>]*>"; "") | gsub("\\s+"; " ")[0:500]) else .body.content[0:500] end),
                attendees: [.attendees[]?.emailAddress.address],
                isOnline: .isOnlineMeeting,
                link: .onlineMeeting.joinUrl,
                organizer: .organizer.emailAddress.address
            } end'
        ;;
    
    create)
        # Create event on owner's calendar
        SUBJECT="$2"
        START="$3"
        END="$4"
        LOCATION="${5:-}"
        
        if [ -z "$SUBJECT" ] || [ -z "$START" ] || [ -z "$END" ]; then
            echo "Usage: outlook-calendar.sh create <subject> <start> <end> [location]"
            echo "Date format: YYYY-MM-DDTHH:MM (e.g., 2026-01-26T10:00)"
            echo "Timezone: $TIMEZONE"
            exit 1
        fi
        
        # Build event JSON safely with jq
        if [ -n "$LOCATION" ]; then
            EVENT_JSON=$(jq -n \
                --arg subj "$SUBJECT" \
                --arg start "$START" \
                --arg end "$END" \
                --arg tz "$TIMEZONE" \
                --arg loc "$LOCATION" \
                '{
                    subject: $subj,
                    start: { dateTime: $start, timeZone: $tz },
                    end: { dateTime: $end, timeZone: $tz },
                    location: { displayName: $loc }
                }')
        else
            EVENT_JSON=$(jq -n \
                --arg subj "$SUBJECT" \
                --arg start "$START" \
                --arg end "$END" \
                --arg tz "$TIMEZONE" \
                '{
                    subject: $subj,
                    start: { dateTime: $start, timeZone: $tz },
                    end: { dateTime: $end, timeZone: $tz }
                }')
        fi
        
        RESULT=$(curl -s "$API/calendar/events" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$EVENT_JSON")
        
        echo "$RESULT" | jq 'if .error then {error: .error.message} else {status: "event created", subject: .subject, start: .start.dateTime[0:16], end: .end.dateTime[0:16], timezone: "'"$TIMEZONE"'", id: .id[-20:]} end'
        ;;
    
    quick)
        # Quick event (1 hour from now or specified time)
        SUBJECT="$2"
        START_TIME="${3:-}"
        
        if [ -z "$SUBJECT" ]; then
            echo "Usage: outlook-calendar.sh quick <subject> [start-time]"
            echo "If no time given, creates 1-hour event starting now"
            echo "Timezone: $TIMEZONE"
            exit 1
        fi
        
        if [ -z "$START_TIME" ]; then
            START=$(TZ="$TIMEZONE" date +"%Y-%m-%dT%H:%M")
            END=$(TZ="$TIMEZONE" date -d "+1 hour" +"%Y-%m-%dT%H:%M" 2>/dev/null || TZ="$TIMEZONE" date -v+1H +"%Y-%m-%dT%H:%M")
        else
            START="$START_TIME"
            END=$(date -d "$START_TIME + 1 hour" +"%Y-%m-%dT%H:%M" 2>/dev/null || echo "$START_TIME")
        fi
        
        EVENT_JSON=$(jq -n \
            --arg subj "$SUBJECT" \
            --arg start "$START" \
            --arg end "$END" \
            --arg tz "$TIMEZONE" \
            '{
                subject: $subj,
                start: { dateTime: $start, timeZone: $tz },
                end: { dateTime: $end, timeZone: $tz }
            }')

        RESULT=$(curl -s "$API/calendar/events" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$EVENT_JSON")
        
        echo "$RESULT" | jq 'if .error then {error: .error.message} else {status: "quick event created", subject: .subject, start: .start.dateTime[0:16], end: .end.dateTime[0:16], timezone: "'"$TIMEZONE"'", id: .id[-20:]} end'
        ;;
    
    delete)
        # Delete event from owner's calendar
        EVENT_ID="$2"
        FULL_ID=$(find_full_event_id "$EVENT_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Event not found"}'
            exit 1
        fi
        
        RESULT=$(curl -s -w "\n%{http_code}" -X DELETE "$API/calendar/events/$FULL_ID" \
            -K "$AUTH_HEADER_FILE")
        
        HTTP_CODE=$(echo "$RESULT" | tail -1)
        if [ "$HTTP_CODE" = "204" ]; then
            echo "{\"status\": \"event deleted\", \"id\": \"$EVENT_ID\"}"
        else
            echo "$RESULT" | head -n -1 | jq '.error // .'
        fi
        ;;
    
    update)
        # Update event on owner's calendar
        EVENT_ID="$2"
        FIELD="$3"
        VALUE="$4"
        
        if [ -z "$FIELD" ] || [ -z "$VALUE" ]; then
            echo "Usage: outlook-calendar.sh update <id> <field> <value>"
            echo "Fields: subject, location, start, end"
            exit 1
        fi
        
        FULL_ID=$(find_full_event_id "$EVENT_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Event not found"}'
            exit 1
        fi
        
        # Build update JSON safely with jq
        case "$FIELD" in
            subject)
                UPDATE_JSON=$(jq -n --arg val "$VALUE" '{ subject: $val }')
                ;;
            location)
                UPDATE_JSON=$(jq -n --arg val "$VALUE" '{ location: { displayName: $val } }')
                ;;
            start)
                UPDATE_JSON=$(jq -n --arg val "$VALUE" --arg tz "$TIMEZONE" '{ start: { dateTime: $val, timeZone: $tz } }')
                ;;
            end)
                UPDATE_JSON=$(jq -n --arg val "$VALUE" --arg tz "$TIMEZONE" '{ end: { dateTime: $val, timeZone: $tz } }')
                ;;
            *)
                echo '{"error": "Unknown field: '"$FIELD"'", "valid_fields": ["subject", "location", "start", "end"]}'
                exit 1
                ;;
        esac
        
        curl -s -X PATCH "$API/calendar/events/$FULL_ID" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$UPDATE_JSON" | jq 'if .error then {error: .error.message} else {status: "event updated", subject: .subject, start: .start.dateTime[0:16], end: .end.dateTime[0:16], id: .id[-20:]} end'
        ;;
    
    calendars)
        # List owner's calendars
        curl -s "$API/calendars" \
            -K "$AUTH_HEADER_FILE" | jq 'if .error then {error: .error.message} else (.value[] | {name: .name, color: .color, canEdit: .canEdit, owner: .owner.address, id: .id[-20:]}) end'
        ;;
    
    free)
        # Check owner's free/busy for a time range
        START="$2"
        END="$3"
        
        if [ -z "$START" ] || [ -z "$END" ]; then
            echo "Usage: outlook-calendar.sh free <start> <end>"
            echo "Date format: YYYY-MM-DDTHH:MM"
            echo "Timezone: $TIMEZONE"
            exit 1
        fi
        
        # Query with timezone
        curl -s "$API/calendarView?startDateTime=$START&endDateTime=$END&\$select=subject,start,end" \
            -K "$AUTH_HEADER_FILE" \
            -H "Prefer: outlook.timezone=\"$TIMEZONE\"" | jq 'if .error then {error: .error.message} else (if (.value | length) == 0 then {status: "free", owner: "'"$OWNER_EMAIL"'", start: "'"$START"'", end: "'"$END"'", timezone: "'"$TIMEZONE"'"} else {status: "busy", owner: "'"$OWNER_EMAIL"'", events: [.value[] | {subject: .subject, start: .start.dateTime[0:16], end: .end.dateTime[0:16]}], timezone: "'"$TIMEZONE"'"} end) end'
        ;;
    
    whoami)
        # Show calendar delegate info
        DELEGATE_EMAIL=$(jq -r '.delegate_email // "unknown"' "$CONFIG_FILE" 2>/dev/null)
        echo "{\"delegate\": \"$DELEGATE_EMAIL\", \"accessing_calendar\": \"$OWNER_EMAIL\", \"timezone\": \"$TIMEZONE\", \"mode\": \"delegate\"}"
        ;;
    
    *)
        echo "Outlook Calendar - Delegate Access"
        echo "Accessing calendar: $OWNER_EMAIL"
        echo "Timezone: $TIMEZONE"
        echo ""
        echo "Usage: outlook-calendar.sh <command> [args]"
        echo ""
        echo "VIEW:"
        echo "  events [count]            - List upcoming events"
        echo "  today                     - Today's events (timezone-aware)"
        echo "  week                      - This week's events"
        echo "  read <id>                 - Event details"
        echo "  calendars                 - List all calendars"
        echo "  free <start> <end>        - Check availability"
        echo ""
        echo "CREATE:"
        echo "  create <subj> <start> <end> [loc] - Create event"
        echo "  quick <subject> [time]    - Quick 1-hour event"
        echo ""
        echo "MANAGE:"
        echo "  update <id> <field> <val> - Update event"
        echo "  delete <id>               - Delete event"
        echo ""
        echo "INFO:"
        echo "  whoami                    - Show delegate info"
        echo ""
        echo "Date format: YYYY-MM-DDTHH:MM (e.g., 2026-01-26T10:00)"
        echo "All times use configured timezone: $TIMEZONE"
        ;;
esac
