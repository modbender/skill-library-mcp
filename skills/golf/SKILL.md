---
name: Golf
slug: golf
version: 1.0.0
homepage: https://clawic.com/skills/golf
description: Track rounds, handicap, clubs, and courses with personalized improvement tips.
metadata: {"clawdbot":{"emoji":"⛳","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User wants to track their golf game, log rounds, manage handicap, remember course details, or get personalized practice recommendations based on their history.

## Architecture

Memory lives in `~/golf/`. See `memory-template.md` for setup.

```
~/golf/
├── memory.md          # HOT: handicap, clubs, goals, preferences
├── rounds.md          # WARM: round log with scores, stats
├── courses.md         # WARM: saved courses with notes
└── archive/           # COLD: past seasons
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Clubs guide | `clubs.md` |
| Rules reference | `rules.md` |

## Core Rules

### 1. Check Memory First
Before any recommendation, read `~/golf/memory.md` for:
- Current handicap index
- Club distances
- Known weaknesses
- Practice focus areas

### 2. Log Rounds Proactively
After user reports a round, update `~/golf/rounds.md`:

| Date | Course | Tees | Score | GIR | FIR | Putts | Notes |
|------|--------|------|-------|-----|-----|-------|-------|
| YYYY-MM-DD | Name | White | 85 | 7/18 | 9/14 | 32 | Driver issues |

### 3. Track Patterns
Analyze rounds.md to identify:
- Consistent misses (slice, hook, short-sided)
- Scoring zones (par 3s vs par 5s)
- Putting trends (3-putts, distance)

### 4. Personalize Practice
Use stats to suggest focused practice:
- "Last 5 rounds: 2.1 putts/GIR → work on lag putting"
- "FIR 50% with driver → consider 3-wood off tee"

### 5. Update Handicap
After posting rounds, recalculate handicap differential:
```
Differential = (Score - Course Rating) x 113 / Slope
```

## Golf Traps

- Generic swing tips → reference their specific miss pattern
- Ignoring conditions → factor wind, wet, altitude
- Club suggestions without knowing their bag → check inventory
- Forgetting course notes → review courses.md before rounds

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `plan` — trip planning
- `remind` — tee time reminders

## Feedback

- If useful: `clawhub star golf`
- Stay updated: `clawhub sync`
