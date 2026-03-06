#!/bin/bash

CALENDAR_NAME="$1"
EVENT_SUMMARY="$2"
EVENT_DESCRIPTION="$3"
RELATIVE_START_DATE="$4"
START_TIME="$5"
RELATIVE_END_DATE="$6"
END_TIME="$7"

# Парсим относительную дату начала
START_DATETIME_FORMATTED=$(skills/apple-calendar-manager/parse_relative_date.sh "$RELATIVE_START_DATE" "$START_TIME")
if [ $? -ne 0 ]; then
    echo "Error parsing start date." >&2
    exit 1
fi

# Парсим относительную дату окончания
END_DATETIME_FORMATTED=$(skills/apple-calendar-manager/parse_relative_date.sh "$RELATIVE_END_DATE" "$END_TIME")
if [ $? -ne 0 ]; then
    echo "Error parsing end date." >&2
    exit 1
fi

# Вызываем основной скрипт AppleScript для добавления события
osascript skills/apple-calendar-manager/add_event.scpt \
    "$CALENDAR_NAME" \
    "$EVENT_SUMMARY" \
    "$EVENT_DESCRIPTION" \
    "$START_DATETIME_FORMATTED" \
    "$END_DATETIME_FORMATTED"