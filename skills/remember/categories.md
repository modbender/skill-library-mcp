# Memory Categories (Adapt to Your Domain)

## Core Categories (Universal)

### commitments.md
```markdown
# Commitments

## Active
- [ ] [2026-02-15] Deploy v2 to production | confidence:certain
- [ ] [2026-02-12] Send updated design to Maria | source:explicit

## Completed (archive after 30 days)
- [x] [2026-02-10] Fix authentication bug
```

### preferences.md
```markdown
# Preferences

## Communication
- Concise responses | source:explicit | 2026-01-15
- Spanish casual, English technical | source:inferred

## Work Style  
- No Prettier | source:explicit (corrected me twice)
- Minimal dependencies | source:pattern
```

### corrections.md
```markdown
# Corrections (Mistakes Not to Repeat)

## Explicit
- [2026-02-01] Never suggest Vercel — user self-hosts | confidence:certain
- [2026-01-20] Don't auto-commit without asking | confidence:certain

## Learned
- [2026-02-05] Always show screenshots before UI changes | source:feedback pattern
```

### decisions.md
```markdown
# Decisions

## Architecture
- [2026-01-10] SQLite over Postgres — offline-first MVP | reasoning:simplicity
- [2026-02-01] No custom backend until scale | reasoning:speed to market

## Process
- [2026-02-05] PRD before implementation | source:explicit directive
```

### relationships.md
```markdown
# People

## Ivan
- Role: Owner
- Preferences: Autonomy, directness
- Updated: 2026-02-10

## Maria  
- Role: Designer on ClawMsg
- Context: Prefers visual mockups
- Updated: 2026-02-01
- [Note: Check if still on project]
```

## Domain-Specific Extensions

### For Coding Work
Add: `environments.md` (servers, ports, keys locations), `debugging.md` (error patterns)

### For Writing Work
Add: `voices/` folder (per-client tone), `audiences.md`, `style-guides/`

### For Personal Assistant
Add: `calendar.md`, `health.md` (with privacy flag), `family.md`, `routines.md`

## File Size Guidelines

- Over 50 entries? Split into sub-files or archive old items
- Over 100 entries? You're hoarding, not curating — prune harder
