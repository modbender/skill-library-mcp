# Memory Template — YouTube Video Transcript

Create `~/youtube-video-transcript/memory.md` with this structure. Always inform the user when saving preferences.

```markdown
# YouTube Video Transcript Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
caching_consent: pending | yes | no

## Preferences

### Format
output: markdown
timestamps: always
summaries: detailed

### Behavior
auto_cache: false
export_location: ~/youtube-video-transcript/exports/

## Recent Videos

| Date | Video | Channel | Action |
|------|-------|---------|--------|
| YYYY-MM-DD | [Title](url) | Channel | transcript/summary |

## Favorite Channels

- Channel Name — topic focus

## Notes

---
*Updated: YYYY-MM-DD*
```

## Video Cache Structure

For each processed video (only with user consent), create `~/youtube-video-transcript/videos/{video_id}.md`:

```markdown
# {Video Title}

**Video ID:** {id}
**URL:** https://youtube.com/watch?v={id}
**Channel:** {channel_name}
**Duration:** {HH:MM:SS}
**Extracted:** YYYY-MM-DD

## Metadata
- **Published:** YYYY-MM-DD
- **Views:** {count}
- **Language:** {subtitle_language}
- **Subtitle Type:** manual | auto-generated

## Chapters

| Time | Chapter |
|------|---------|
| 00:00 | Introduction |
| 03:45 | Main Topic |

## Transcript

[00:00] First segment text...
[00:15] Second segment text...

## User Notes

---
*Cached: YYYY-MM-DD*
```

## Consent Management

| Field | Meaning | Behavior |
|-------|---------|----------|
| `caching_consent: pending` | Not asked yet | Ask on first use |
| `caching_consent: yes` | User agreed | Cache transcripts |
| `caching_consent: no` | User declined | Never cache without asking again |

## Transparency Principles

- **Always confirm** what you're saving: "I'll remember you prefer detailed summaries"
- **Show location** when caching: "Saved transcript to ~/youtube-video-transcript/videos/abc123.md"
- **Offer to show** saved files anytime
- **Delete on request** with confirmation: "Deleted the transcript. Want me to also clear your preferences?"
