# Memory Template — Udio

Create `~/udio/memory.md` with this structure:

```markdown
# Udio Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Approach
method: api | browser | prompt-only
wrapper: python | node | none
token_location: keychain:udio_auth_token | env:UDIO_AUTH_TOKEN | none

## Preferences

### Genres
<!-- Primary genres they gravitate toward -->

### Voice
<!-- Male, female, instrumental, specific vocal styles -->

### Production
<!-- Lo-fi, polished, vintage, modern, etc -->

### Purpose
<!-- Content creation, personal, commercial -->

## Successful Patterns

### Prompts That Worked
<!-- Copy exact prompts that produced good results -->
| Prompt | Seed | Result |
|--------|------|--------|

### Seeds to Remember
<!-- Seed numbers associated with good generations -->

## Projects

### Active
<!-- Current music projects with settings -->

### Completed
<!-- Past projects for reference -->

## Notes
<!-- Observations about their style, what to avoid -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning preferences | Gather info opportunistically |
| `complete` | Knows their style well | Generate confidently |
| `paused` | User said "not now" | Work with what you have |

## Approach Values

| Value | When to Use |
|-------|-------------|
| `api` | User has wrapper installed and token |
| `browser` | User prefers visual interaction or no API setup |
| `prompt-only` | User just wants help crafting prompts |

## Per-Project Tracking

For larger projects, create `~/udio/projects/{project-name}.md`:

```markdown
# {Project Name}

## Goal
<!-- What they're creating -->

## Style Profile
genre: 
mood:
tempo:
voice:

## Tracks
| # | Title | Prompt | Seed | Status | URL |
|---|-------|--------|------|--------|-----|
| 1 | Intro | ... | 12345 | done | https://... |
| 2 | Main | ... | -1 | pending | |

## Notes
<!-- Project-specific observations -->
```

## Key Principles

- **Never store auth tokens** — only reference location
- Learn preferences from behavior, don't interrogate
- Save successful prompts verbatim with seeds
- Track what they reject to avoid similar suggestions
- Organize by project for multi-song work
