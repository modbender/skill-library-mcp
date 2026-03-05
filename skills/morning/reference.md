# Morning Skill Reference

## Required File Structure

```
workspace/
├── journal/
│   └── YYYY/
│       ├── goals.md          # Annual goals — see template below
│       └── MM/
│           └── YYYY-MM-DD.md # Daily entries — see template below
├── plan.md                   # Long-term plan (optional but recommended)
└── inbox.md                  # Quick capture
```

The skill installs to `~/.claude/skills/morning/` and reads files via `../../` (two levels up). If your workspace is elsewhere, update the paths in SKILL.md.

---

## File Templates

### Annual Goals (`journal/YYYY/goals.md`)

```markdown
# YYYY

**[Your one-sentence annual theme]**

---

### Goal Category 1
- [ ] Outcome 1
- [ ] Outcome 2

### Goal Category 2
- [ ] Outcome 1

---

## Anti-goals

- Things you're explicitly NOT doing this year

---

## Becoming

- The kind of person you're becoming this year
```

### Daily Journal (`journal/YYYY/MM/YYYY-MM-DD.md`)

```markdown
# YYYY-MM-DD

## Morning (Franklin: "What good shall I do this day?")
- [ ] Key outcome 1 (connects to: [annual goal])
- [ ] Key outcome 2

## Log
-

## Active Projects
1. [project name — status]

## Active Decisions
- [ ] [open decision]
```

### Inbox (`inbox.md`)

```markdown
# Inbox

Quick capture. Process later.

---

## To Do

- [ ] Item

## Someday / Not Now

-

## Ideas

-
```

---

## Optional: Calendar Integration (macOS)

Install `icalBuddy` to pull today's calendar events into the morning routine:

```bash
brew install ical-buddy
```

Add to Step 3 of the morning skill to auto-populate today's events:

```bash
icalBuddy -nc -nrd -eep "notes,location,url,attendees" -tf "%H:%M" -df "" eventsToday
```

Filter to specific calendars with `-ic "Work,Personal"`.

---

## Decisions Directory (optional)

Create a `decisions/` folder next to the skill for structured decision records:

```
decisions/
└── YYYY-MM-DD-decision-title.md
```

Each decision file should include a `status:` field (Open / Active / Closed) so the skill can surface relevant ones during the morning check.
