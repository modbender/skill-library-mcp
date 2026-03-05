# Calendar

## Events

```bash
# Create event
curl -s "${BITRIX24_WEBHOOK_URL}calendar.event.add.json" \
  -d 'type=user&ownerId=1&name=Team Meeting&description=Weekly sync&from=2026-03-01T10:00:00&to=2026-03-01T11:00:00&section=1' | jq .result

# List events for a date range
curl -s "${BITRIX24_WEBHOOK_URL}calendar.event.get.json" \
  -d 'type=user&ownerId=1&from=2026-03-01&to=2026-03-31' | jq .result

# Get event by ID
curl -s "${BITRIX24_WEBHOOK_URL}calendar.event.getbyid.json" -d 'id=123' | jq .result

# Update event
curl -s "${BITRIX24_WEBHOOK_URL}calendar.event.update.json" \
  -d 'id=123&name=Updated Meeting&from=2026-03-01T14:00:00&to=2026-03-01T15:00:00' | jq .result

# Delete event
curl -s "${BITRIX24_WEBHOOK_URL}calendar.event.delete.json" -d 'id=123' | jq .result
```

## Event with Attendees

```bash
curl -s "${BITRIX24_WEBHOOK_URL}calendar.event.add.json" \
  -d 'type=user&ownerId=1&name=Project Review&from=2026-03-05T15:00:00&to=2026-03-05T16:00:00&attendees[]=1&attendees[]=2&attendees[]=3&importance=high' | jq .result
```

## Recurring Events

```bash
curl -s "${BITRIX24_WEBHOOK_URL}calendar.event.add.json" \
  -d 'type=user&ownerId=1&name=Daily Standup&from=2026-03-01T09:00:00&to=2026-03-01T09:15:00&rrule[FREQ]=DAILY&rrule[COUNT]=30' | jq .result
```

**RRULE FREQ values:** `DAILY`, `WEEKLY`, `MONTHLY`, `YEARLY`.

## Calendar Sections

```bash
# List user's calendar sections
curl -s "${BITRIX24_WEBHOOK_URL}calendar.section.get.json" \
  -d 'type=user&ownerId=1' | jq .result
```

## Busy/Free Check

```bash
curl -s "${BITRIX24_WEBHOOK_URL}calendar.accessibility.get.json" \
  -d 'users[]=1&users[]=2&from=2026-03-01&to=2026-03-02' | jq .result
```

## Reference

**Event types:** `user` (personal), `group` (workgroup), `company_calendar` (company-wide).

**Key fields:** name, description, from, to, section, attendees[], color, importance (high/normal), location, rrule, remind[].

**Importance:** `high`, `normal`.

## More Methods (MCP)

This file covers common calendar methods. For additional methods or updated parameters, use MCP:
- `bitrix-search "calendar event"` — find all calendar methods
- `bitrix-method-details calendar.event.add` — get full spec for any method
