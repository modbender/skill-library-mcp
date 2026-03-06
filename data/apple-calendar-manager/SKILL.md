---
name: apple-calendar-manager
description: Manage Apple Calendar events via AppleScript. Create, edit, delete, and search calendar events.
---

# Apple Calendar Manager

This skill allows OpenClaw to manage events in Apple Calendar using AppleScript.

## Capabilities

-   Add new events to a specified calendar with smart date parsing (e.g., "today", "tomorrow", "next Monday").
-   (Future) Edit existing events.
-   (Future) Delete events.
-   (Future) Search for events.

## Requirements

-   macOS
-   Apple Calendar application must be accessible and authorized for automation.
-   The calendar name must exist in the user's Calendar app.

## Usage

### Add an Event (Smart Date Parsing)

Use the `add_event_smart.sh` script to add events with relative dates or explicit dates.

**Arguments:**
1.  `calendar_name`: The name of the calendar (e.g., "Рабочий", "Домашний").
2.  `event_summary`: The title of the event.
3.  `event_description`: (Optional) Description for the event.
4.  `relative_start_date`: Relative date for start (e.g., "today", "tomorrow", "day after tomorrow", "понедельник", "next monday") or absolute date (e.g., "2026-02-23").
5.  `start_time`: Start time (format HH:MM, e.g., "12:00").
6.  `relative_end_date`: Relative date for end (same as `relative_start_date`).
7.  `end_time`: End time (format HH:MM, e.g., "15:00").

**Example:**
`skills/apple-calendar-manager/add_event_smart.sh "Рабочий" "Чай с Настей" "Чай с Настей с 12 до 15" "tomorrow" "12:00" "tomorrow" "15:00"`

### Add an Event (Absolute Date Parsing)

Use the `add_event.scpt` script directly if you prefer to provide absolute dates in `YYYYMMDDHHMMSS` format.

**Arguments:**
1.  `calendar_name`: The name of the calendar.
2.  `event_summary`: The title of the event.
3.  `event_description`: Description for the event.
4.  `start_datetime_formatted`: Start date and time in `YYYYMMDDHHMMSS` format.
5.  `end_datetime_formatted`: End date and time in `YYYYMMDDHHMMSS` format.

**Example:**
`osascript skills/apple-calendar-manager/add_event.scpt "Рабочий" "Тест скилла Календарь" "Тестовое событие" "20260225140000" "20260225150000"`

## Implementation Details

-   Uses `osascript` for direct Apple Calendar application control.
-   `parse_relative_date.sh` script handles conversion of relative date strings to absolute date/time formats required by AppleScript.
-   Requires Apple Calendar.app to be running and accessible.
-   macOS-only.
