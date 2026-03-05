# Memory Template — Skill Builder / Creator

**Optional:** If user wants to track projects, they can create `~/skill-builder/projects.md`.

Ask user before creating any files. Template:

```markdown
# Skill Projects

## Active

### [skill-name]
- status: drafting | reviewing | ready
- goal: [one sentence]
- files: SKILL.md, setup.md, [others]
- notes: [observations, decisions]
- last: YYYY-MM-DD

## Completed

### [skill-name]
- published: YYYY-MM-DD
- version: X.Y.Z
- lessons: [what worked, what to improve]

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning |
|-------|---------|
| `drafting` | Writing initial content |
| `reviewing` | Checking structure, testing |
| `ready` | Ready to publish |

## Usage

- Add new project when user starts skill
- Update status as work progresses
- Move to Completed after publish
- Capture lessons for future skills
