# Memory Template — Skill Finder

Create `~/skill-finder/memory.md` with this structure:

```markdown
# Skill Finder Memory

## Status
status: ongoing
last: YYYY-MM-DD

## Preferences
<!-- Explicit quality values stated by user -->
<!-- Examples: "prefers minimal", "wants well-maintained", "okay with experimental" -->

## Liked
<!-- Skills user explicitly praised, with their reason -->
<!-- Format: slug — "what they said they liked" -->

## Passed
<!-- Skills user explicitly declined, with their reason -->
<!-- Format: slug — "what they said was wrong" -->

## Domains
<!-- Areas user works in (helps narrow searches) -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning |
|-------|---------|
| `ongoing` | Still learning preferences |
| `established` | Has enough preference data |

## What to Store

### Preferences (from explicit statements)
- "I prefer minimal skills" → add verbatim
- "I want well-maintained only" → add verbatim
- "I don't mind experimental" → add verbatim

### Liked (from explicit praise)
- User says "this skill is great because X" → `slug — "X"`
- User expresses satisfaction → `slug — "reason"`

### Passed (from explicit rejection)
- User declines with reason → `slug — "reason"`
- User uninstalls and explains → `slug — "reason"`

## What NOT to Store

- Silent installations (no comment = no data)
- Inferred preferences from behavior patterns
- Anything not explicitly stated by user

## Using Memory

When multiple skills match a search:
1. **Check Passed** — exclude similar
2. **Check Liked** — favor similar qualities
3. **Apply Preferences** — filter accordingly

## Maintenance

Keep under 50 lines. When exceeded:
- Archive old Liked/Passed entries
- Keep most recent Preferences
