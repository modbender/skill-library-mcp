---
name: student-timetable
description: Student timetable manager for self or parent-managed child profiles. Includes init flow + profile registry under schedules/profiles/.
---

# student-timetable

Design

- Supports two operating modes:
  - Self profile: a student manages their own schedule.
  - Child profiles: a parent/guardian manages one or more children.
- Uses a profile registry + per-profile data files so queries are consistent across kids and reusable in other automations.

Initialize

- Run interactive setup:
  - `node skills/student-timetable/cli.js init`
- This writes/updates:
  - `schedules/profiles/registry.json`
  - `schedules/profiles/<profile_id>/*`

Query

- `node skills/student-timetable/cli.js today --profile <id|name|alias>`
- `node skills/student-timetable/cli.js tomorrow --profile <id|name|alias>`
- `node skills/student-timetable/cli.js this_week --profile <id|name|alias>`
- `node skills/student-timetable/cli.js next_week --profile <id|name|alias>`

Tool entry

- `tool.js`
