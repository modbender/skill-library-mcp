---
name: afrexai-email-to-calendar
version: 1.0.0
description: >
  Extract calendar events, deadlines, action items, and follow-ups from emails.
  Works with any calendar provider (Google, Outlook, Apple, Notion, etc.).
  No external dependencies — pure agent intelligence.
  Use when the user forwards an email, asks to check inbox for events,
  or wants to extract structured scheduling data from any text.
---

# Email → Calendar Extraction Engine

Turn emails into structured calendar events with zero missed deadlines.

## Quick Start

When you receive an email (forwarded, pasted, or from inbox):

1. **Parse** — Extract every time-relevant item using the framework below
2. **Classify** — Score each item by type and confidence
3. **Present** — Show structured results with numbered selection
4. **Create** — Use the user's calendar tool to create confirmed events
5. **Follow up** — Track deadlines and send reminders

---

## 1. Extraction Framework

### What to Look For

Scan every email for ALL of these categories:

| Category | Signals | Priority |
|----------|---------|----------|
| **Hard Events** | "meeting at", "call on", "event on", specific date+time | 🔴 High |
| **Deadlines** | "due by", "submit before", "RSVP by", "register by", "expires" | 🔴 High |
| **Soft Events** | "sometime next week", "let's meet soon", "planning for March" | 🟡 Medium |
| **Recurring** | "every Monday", "weekly", "monthly", "standing meeting" | 🟡 Medium |
| **Action Items** | "please review", "can you send", "follow up on", "action required" | 🟡 Medium |
| **Travel/Logistics** | Flight numbers, hotel confirmations, check-in times, gate info | 🔴 High |
| **Implicit Deadlines** | Event is Feb 20 → ticket deadline is likely 1-2 weeks before | 🟡 Medium |

### Extraction Template

For each item found, extract:

```yaml
- title: "Descriptive name (max 80 chars)"
  type: event | deadline | action_item | travel | recurring
  date: "YYYY-MM-DD"
  day_of_week: "Monday"  # Always include for verification
  time_start: "14:00"    # 24h format, default 09:00 if unclear
  time_end: "15:00"      # Default: start + 1h for meetings, all-day for deadlines
  timezone: "America/New_York"  # Extract from email headers or content
  is_all_day: false
  is_multi_day: false     # If true, include end_date
  end_date: null
  recurrence: null        # "weekly" | "biweekly" | "monthly" | "MWF" | custom RRULE
  location: null          # Physical address or video link
  url: null               # Registration link, event page, or action URL
  attendees: []           # Names/emails mentioned
  confidence: high | medium | low
  source_quote: "exact text from email that indicates this event"
  notes: "any context the user should know"
  deadline_action: null   # "RSVP" | "register" | "buy tickets" | "submit"
  deadline_url: null      # Direct link to take action
  reminder_minutes: 30    # Suggested reminder (15 for calls, 60 for travel, 1440 for deadlines)
```

### Confidence Scoring

| Confidence | Criteria |
|------------|----------|
| **High** | Explicit date + time + clear event type. E.g. "Meeting on Feb 15 at 2pm" |
| **Medium** | Date but no time, or time but approximate date. E.g. "next Tuesday afternoon" |
| **Low** | Vague reference. E.g. "we should catch up soon", "sometime in March" |

### Smart Defaults

- **No time given for meeting** → 09:00-10:00 (mark confidence: medium)
- **No time given for deadline** → 23:59 (end of day)
- **No timezone** → Use user's default timezone, note assumption
- **"Morning"** → 09:00, **"Afternoon"** → 14:00, **"Evening"** → 18:00, **"EOD"** → 17:00
- **"Next week"** → Following Monday (mark confidence: medium)
- **Multi-day event** → Set is_multi_day: true, include start and end dates

---

## 2. Email Classification

Before extracting, classify the email:

| Email Type | How to Handle |
|------------|---------------|
| **Calendar notification** (from calendar-notification@google.com, outlook, etc.) | SKIP — these are responses to existing events |
| **Newsletter/marketing** | Extract only if contains relevant event dates |
| **Personal/work email** | Full extraction |
| **Travel confirmation** | Extract ALL logistics: flights, hotels, car rentals, check-ins |
| **Meeting invite** (ICS attachment or structured invite) | Extract directly, high confidence |
| **Thread/reply** | Only extract NEW events, not ones from quoted text |
| **Forwarded email** | Process the forwarded content, note original sender |

### Ignore Patterns (Skip These)

- Automated calendar responses (Accepted, Declined, Tentative)
- Unsubscribe confirmations
- Read receipts
- Auto-replies / Out of office
- Spam/promotional (unless user explicitly forwards it)

---

## 3. Presentation Format

Always present extracted items in this format:

```
📧 From: [sender] | Subject: [subject] | Date: [received date]

Found [N] calendar items:

1. 🔴 **Team Standup** — Mon Feb 17, 9:00-9:30 AM EST
   📍 Zoom (link in email) | 👥 Alice, Bob, Charlie
   🔁 Recurring: Every weekday
   ✅ Confidence: High

2. 🔴 **Project Deadline: Q1 Report** — Fri Feb 28, EOD
   ⚠️ ACTION REQUIRED: Submit report
   🔗 [Submission portal](url)
   ⏰ Suggested reminder: 3 days before
   ✅ Confidence: High

3. 🟡 **Team Lunch** — "sometime next week"
   📍 TBD
   ⚠️ Confidence: Medium — date needs confirmation

---
Reply with numbers to create (e.g. "1, 2"), "all", or "none".
Type "edit 3" to modify before creating.
```

### Presentation Rules

1. **Always show day of week** — humans verify dates by day name
2. **Group by date** when >5 items
3. **Flag conflicts** — if new event overlaps existing calendar
4. **Highlight deadlines** with ⚠️ and days remaining
5. **Show source quote** for medium/low confidence items
6. **Never auto-create** without user confirmation

---

## 4. Calendar Creation

After user confirms, create events using their calendar tool:

### Google Calendar (via `gog` or API)
```bash
gog calendar create \
  --title "Event Title" \
  --start "2026-02-17T09:00:00-05:00" \
  --end "2026-02-17T10:00:00-05:00" \
  --description "Extracted from email: [subject]" \
  --location "Zoom link or address"
```

### Apple Calendar (via `osascript`)
```bash
osascript -e 'tell application "Calendar"
  tell calendar "Work"
    make new event with properties {summary:"Event Title", start date:date "Monday, February 17, 2026 at 9:00:00 AM", end date:date "Monday, February 17, 2026 at 10:00:00 AM", description:"Extracted from email", location:"Zoom"}
  end tell
end tell'
```

### Notion / Other
- Format as structured data and use the appropriate API
- Or output as .ics file the user can import anywhere

### ICS Export (Universal)
```
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:20260217T090000
DTEND:20260217T100000
SUMMARY:Event Title
DESCRIPTION:Extracted from email
LOCATION:Zoom link
END:VEVENT
END:VCALENDAR
```

---

## 5. Duplicate Detection

Before creating any event, check for duplicates:

1. **Search calendar** for events on the same date with similar title (fuzzy match)
2. **Check tracking file** — maintain a log of created events:

```json
// memory/email-calendar-log.json
{
  "created_events": [
    {
      "email_id": "msg-123",
      "email_subject": "Team Offsite",
      "event_title": "Team Offsite",
      "event_date": "2026-02-17",
      "calendar_event_id": "cal-456",
      "created_at": "2026-02-13T10:00:00Z"
    }
  ]
}
```

3. **If duplicate found**: Show user and ask — "This looks similar to [existing event]. Skip, update, or create anyway?"

---

## 6. Deadline & Reminder Engine

### Deadline Patterns to Detect

| Pattern | Example | Action |
|---------|---------|--------|
| RSVP deadline | "RSVP by Feb 10" | Create reminder 3 days before |
| Registration | "Register by March 1" | Create reminder 1 week before |
| Early bird | "Early bird ends Feb 15" | Create reminder 2 days before |
| Ticket sales | "Tickets on sale until..." | Create reminder + calendar event |
| Submission | "Submit proposal by..." | Create reminder 3 days before |
| Expiration | "Offer expires..." | Create reminder 1 day before |

### Reminder Strategy

- **>30 days away**: Remind 1 week before
- **7-30 days away**: Remind 3 days before
- **<7 days away**: Remind 1 day before
- **Deadlines with URLs**: Include the action URL in the reminder
- Create reminder as separate calendar event: "⚠️ DEADLINE: [action] for [event]"

---

## 7. Travel Email Handling

Travel confirmations get special treatment:

### Extract ALL of these:
- ✈️ **Flights**: airline, flight #, departure/arrival times+airports, terminal, gate, confirmation #
- 🏨 **Hotels**: name, address, check-in/out times, confirmation #
- 🚗 **Car rentals**: company, pickup/dropoff times+locations, confirmation #
- 📋 **Transfers**: shuttle times, train bookings

### Create these calendar events:
1. **Flight departure** — include terminal, gate, flight # in description
2. **Flight arrival** — for connecting flights too
3. **Hotel check-in** — with address and confirmation #
4. **Hotel check-out** — with reminder to pack
5. **Car pickup/dropoff** — with location details

### Travel-specific reminders:
- Flight: 3 hours before (domestic), 4 hours before (international)
- Hotel check-out: Morning of departure
- Include all confirmation numbers in event descriptions

---

## 8. Batch Processing

When scanning an inbox for events:

1. **Fetch unread emails** (or emails from last N days)
2. **Filter out noise** — apply ignore patterns
3. **Extract from each** — run extraction framework
4. **Deduplicate across emails** — same event mentioned in multiple threads
5. **Sort by date** — nearest first
6. **Present grouped summary**:

```
📬 Inbox Scan: 47 unread → 12 with calendar items → 18 events found

THIS WEEK (Feb 13-19):
1. 🔴 Sprint Review — Thu Feb 13, 3:00 PM
2. 🔴 1:1 with Manager — Fri Feb 14, 10:00 AM
...

NEXT WEEK (Feb 20-26):
5. 🟡 Team Lunch — date TBD (mentioned in 2 emails)
...

DEADLINES:
⚠️ Q1 Report — Due Feb 28 (15 days) → [Submit here](url)
⚠️ Conference RSVP — Due Feb 20 (7 days) → [RSVP](url)
```

---

## 9. Edge Cases

| Situation | How to Handle |
|-----------|---------------|
| **Multiple timezones in one email** | Extract each event in its stated timezone, convert to user's TZ for display |
| **"TBD" or "TBA" times** | Create all-day event, flag for follow-up |
| **Cancelled events** | Check if already in calendar → offer to delete |
| **Rescheduled events** | Find original → offer to update (not create new) |
| **Recurring with exceptions** | Note specific exception dates in description |
| **Date ambiguity (02/03 = Feb 3 or Mar 2?)** | Use email's locale/origin for MM/DD vs DD/MM, ask if unclear |
| **Events in quoted/forwarded text** | Only process if user explicitly forwarded it |
| **Attachments with .ics files** | Parse ICS directly — highest confidence source |
| **"Save the date" emails** | Create tentative event, mark as placeholder |
| **Conference with multiple sessions** | Extract all sessions as separate events with shared description |

---

## 10. Session Memory

Track user preferences across sessions:

```yaml
# memory/email-calendar-prefs.yaml
default_timezone: "America/New_York"
default_calendar: "Work"
default_reminder_minutes: 30
auto_create_patterns:
  - "standup"
  - "1:1"
ignore_patterns:
  - "newsletter"
  - "marketing"
preferred_format: "12h"  # or "24h"
travel_reminder_hours: 3
```

Update preferences when user corrects you or states a preference.
