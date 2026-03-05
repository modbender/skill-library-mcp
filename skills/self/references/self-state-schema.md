# self-state.json Schema (lightweight)

Path: `memory/self-state.json`

```json
{
  "version": "1.1",
  "last_check_at": "2026-02-22T03:00:00+01:00",
  "last_notable_entry_at": "2026-02-21T18:00:00+01:00",
  "micro_checks_total": 0,
  "entries_written_total": 0,
  "hard_triggers_pending": [],
  "soft_triggers_pending": [],
  "last_weekly_review_at": null,
  "last_monthly_review_at": null
}
```

## Notes

- Keep this file tiny.
- Update `last_check_at` on every micro check.
- Add/remove pending triggers as needed.
- Do not store private user secrets here.
