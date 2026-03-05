# Memory Template — Suno

Create `~/suno/memory.md` with this structure:

```markdown
# Suno Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | web | api | browser

## Generation Method
<!-- How they prefer to generate -->
<!-- web: paste prompts into suno.com -->
<!-- api: aimusicapi.ai or evolink.ai -->
<!-- browser: automated navigation -->

## API Config
<!-- Reference only, not actual keys -->
<!-- e.g., "Using aimusicapi.ai, key in AIMUSICAPI_KEY env var" -->

## Music Preferences
<!-- Genres they like -->
<!-- Typical mood/energy -->
<!-- Vocal preferences -->

## Successful Prompts
<!-- Prompts that produced great results -->
<!-- Format: "prompt" -> result description -->

## Projects
<!-- Ongoing music projects -->
<!-- What they're working on -->

## Notes
<!-- Observations about their taste -->
<!-- Things that worked or didn't -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning |
|-------|---------|
| `ongoing` | Still learning their preferences |
| `complete` | Know their style well |
| `paused` | User said "not now" |

## Integration Values

| Value | Method |
|-------|--------|
| `pending` | Not yet determined |
| `web` | Paste prompts into suno.com |
| `api` | Programmatic via API |
| `browser` | Browser automation |

## Projects Folder

For users with multiple projects, create `~/suno/projects/`:

```markdown
# Project: [Name]

## Concept
[What the project is about]

## Songs
- [Song 1]: prompt used, URL, status
- [Song 2]: prompt used, URL, status

## Style Guide
[Consistent style for this project]
```

## Songs Folder

Optional: `~/suno/songs/` for downloaded audio files.

## Key Principles

- Learn preferences through creation, not interrogation
- Remember what prompts worked for reuse
- Note reactions to different styles
- Never store actual API keys in memory files
- Update `last` date on each session
