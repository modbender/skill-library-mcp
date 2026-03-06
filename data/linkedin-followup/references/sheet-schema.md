# CRM Sheet Schema

Sheet: **LinkedIn Outreach CRM**
ID: `1eEZDGcr1dIbSC782mNkxvD7pVrF8rOFySWCVZ1RXkhM`
Tab: `Sheet1` (rename to `Outreach` when possible)

---

## Full Column Layout (A–P)

| Col | Field             | Written by         | Updated by         |
|-----|-------------------|--------------------|--------------------|
| A   | Date Sent         | linkedin-dm        | —                  |
| B   | Person Name       | linkedin-dm        | —                  |
| C   | Role / Title      | linkedin-dm        | linkedin-followup  |
| D   | Company           | linkedin-dm        | linkedin-followup  |
| E   | LinkedIn URL      | linkedin-dm        | —                  |
| F   | Relationship Hook | linkedin-dm        | —                  |
| G   | Opener Sent       | linkedin-dm        | —                  |
| H   | Pitch Sent        | linkedin-dm        | —                  |
| I   | Campaign          | linkedin-dm        | —                  |
| J   | Status            | linkedin-dm (Sent) | linkedin-followup  |
| K   | Notes             | linkedin-dm        | linkedin-followup  |
| L   | Last Updated      | linkedin-dm        | linkedin-followup  |
| M   | Last Reply Date   | —                  | linkedin-followup  |
| N   | Last Reply (200c) | —                  | linkedin-followup  |
| O   | Conversation Log  | —                  | linkedin-followup  |
| P   | Next Action       | —                  | linkedin-followup  |

---

## Adding Columns M–P (one-time setup)

Run once to add the new column headers:
```bash
gog sheets update 1eEZDGcr1dIbSC782mNkxvD7pVrF8rOFySWCVZ1RXkhM "Sheet1!M1:P1" \
  --values-json '[["Last Reply Date","Last Reply (preview)","Conversation Log","Next Action"]]' \
  --input USER_ENTERED
```

---

## Status Lifecycle

```
Sent
 ├── Replied           ← they responded
 │    ├── Call Scheduled
 │    │    ├── Demo Done
 │    │    │    ├── Closed Won
 │    │    │    └── Closed Lost
 │    │    └── No Response (post-call)
 │    └── Follow Up Sent
 │         └── No Response
 └── No Response       ← never replied after follow-ups
```

---

## Querying the Sheet

### Get all rows as JSON
```bash
gog sheets get 1eEZDGcr1dIbSC782mNkxvD7pVrF8rOFySWCVZ1RXkhM "Sheet1!A:P" --json
```

### Find rows needing follow-up (parse JSON output)
Filter by:
- `status == "Sent"` AND `lastUpdated < (today - 3 days)`
- `status == "Replied"` (needs response)
- `status == "Follow Up Sent"` AND `lastUpdated < (today - 5 days)`

### Update a single cell
```bash
# Update status in row 5
gog sheets update 1eEZDGcr1dIbSC782mNkxvD7pVrF8rOFySWCVZ1RXkhM "Sheet1!J5" \
  --values-json '[["Replied"]]' --input USER_ENTERED
```

### Update multiple cells in a row (e.g. row 5, cols J–P)
```bash
gog sheets update 1eEZDGcr1dIbSC782mNkxvD7pVrF8rOFySWCVZ1RXkhM "Sheet1!J5:P5" \
  --values-json '[["Replied","2026-02-15","2026-02-15T09:30:00","Hey Madhur! Sounds cool, how does it work...","[2026-02-13 17:05 SENT] Hey Rishabh...\n[2026-02-15 09:30 RECEIVED] Hey Madhur!...","Demo offer pending"]]' \
  --input USER_ENTERED
```

---

## Reading Row Numbers

The JSON output from `gog sheets get` is 0-indexed. Row 1 in the sheet = index 0 in JSON (header). So:
- Row 2 (first data row) = JSON index 1
- Row N in sheet = JSON index N-1
- Sheet row number = JSON index + 1

When updating, use the **sheet row number** (e.g. `Sheet1!J2` = row 2 = first data row).

---

## Conversation Log Tips

- Stored as a multi-line string in col O
- Use `\n` as line separator when writing via gog
- When reading, split on `\n` to parse individual entries
- Entries format: `[YYYY-MM-DD HH:MM SENT/RECEIVED] message text`
- Keep entries under 5000 chars total per cell (Google Sheets cell limit is 50,000 chars, but keep it readable)
- For very long threads, truncate old SENT messages after 30 days but keep all RECEIVED messages

---

## Next Action Field (Col P)

Free-text notes for what should happen next. Examples:
- `Demo offer pending — waiting for reply`
- `Scheduled call 2026-02-20 3pm`
- `Sent Loom video — follow up in 2 days`
- `Not interested — archive`
- `Referred to their colleague Priya Singh`
