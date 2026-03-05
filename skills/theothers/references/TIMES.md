## datetime

Used by search_listings tool.

Must be provided in ISO 8601 datetime string format (e.g. 2026-03-15T14:30:00Z)
When datetime is provided to a search query, listings which specify a time range not including the datetime will be excluded from results.

## time_window

Used by create_listing and update_listing tools.

Format: Each part is optional — leave it empty for "no restriction".

### Days — digits 1-7 where 1=Monday, 7=Sunday
  - 12345 = weekdays
  - 67 = weekends
  - 135 = Mon/Wed/Fri

### Hours — 24h range as HHMM-HHMM
  - 0900-1700 = 9am to 5pm
  - 1800-2200 = 6pm to 10pm

### Dates — comma-separated YYYY-MM-DD, and/or a range YYYY-MM-DD..YYYY-MM-DD
  - 2026-03-15 = single date
  - 2026-03-15,2026-03-22 = two specific dates
  - 2026-03-15..2026-03-22 = date range, inclusive

### Full examples:
  - 12345|0900-1700| — weekdays 9-5, any date
  - 67|| — weekends only, any time, any date
  - |1800-2200| — any day, evenings only
  - ||2026-03-15,2026-03-16 — specific dates only
  - || — no restrictions (available anytime)

All three parts combine with AND logic — a searcher's datetime must match all non-empty components of any listing.
