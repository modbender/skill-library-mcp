# StudentTimetable Schema v2 (rules/exceptions/dated_items)

## Files

- schedules/profiles/registry.json
- schedules/profiles/<profile_id>/schedule.json (v2)

## schedule.json structure

{
  "version": 2,
  "profile_id": "zian",
  "timezone": "Asia/Singapore",
  "rules": {
    "weekly_rules": [
      {
        "id": "wr-math-mon-0900",
        "weekday": "mon",
        "start_time": "09:00",
        "end_time": "10:00",
        "title": "Math",
        "location": "",
        "notes": "",
        "tags": ["math"],
        "effective_from": "2026-01-01",
        "effective_to": "2026-03-31"
      }
    ],
    "dated_items": [
      {
        "id": "di-cca-band-20260201",
        "date": "2026-02-01",
        "start_time": "15:00",
        "end_time": "16:30",
        "title": "Band CCA",
        "location": "",
        "notes": "",
        "tags": ["cca"]
      }
    ],
    "weekly_exceptions": [
      {
        "id": "wx-20260223-cancel-math",
        "date": "2026-02-23",
        "kind": "cancel",
        "targets": {
          "rule_ids": ["wr-math-mon-0900"],
          "time_windows": []
        },
        "notes": "No class"
      }
    ]
  },
  "special_events": [
    {
      "id": "ev-chingay-briefing-2026-02-20",
      "date": "2026-02-20",
      "title": "Chingay Briefing",
      "start_time": "",
      "end_time": "",
      "location": "TBD",
      "notes": "time TBD",
      "tags": ["school"],
      "cancels_weekly": false
    }
  ],
  "updated_at": "2026-02-19T09:00:00+08:00"
}

## Semantics

- weekly_rules describe regular recurring items. effective_from/to are optional; when absent they are always active.
- weekly_exceptions apply on a specific date:
  - kind=cancel removes matching rule-derived items for that date.
  - Targeting:
    - Prefer rule_ids.
    - time_windows is a fallback (start/end + optional tags) when rule_id is unknown.
- dated_items are one-off timetable items that are part of the normal schedule but are inherently irregular.
- special_events are separate from timetable rules; they can have TBD time/location. They show up in outputs but do not modify rules unless explicit.
