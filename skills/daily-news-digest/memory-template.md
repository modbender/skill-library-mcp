# Memory Template — Daily News Digest

Create `~/daily-news-digest/memory.md` with this structure:

```markdown
# Daily News Digest Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Interests
<!-- Topics to emphasize, natural language -->
<!-- Example: Tech and AI news, especially startups and product launches -->

## Exclusions
<!-- Topics to filter out -->
<!-- Example: Crypto, celebrity gossip, sports -->

## Geography
<!-- Location and regions of interest -->
<!-- Example: Based in Madrid, also follows US tech scene -->

## Format
<!-- Preferred briefing style -->
<!-- Example: Standard format, 8-10 stories with context -->

## Voice
<!-- Audio preferences -->
<!-- Example: Enabled for morning briefings, uses ElevenLabs -->

## Schedule
<!-- Automated delivery times -->
<!-- Example: Morning briefing at 8am to Telegram, no evening -->

## Sources
<!-- Preferred and blocked sources -->
<!-- Example: Prefer Hacker News, The Verge. Block Daily Mail. -->

## Notes
<!-- Internal observations from behavior -->
<!-- Example: Skips long-form articles, prefers bullet points -->
<!-- Example: Always asks follow-up on AI stories -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Gather context opportunistically |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |
| `never_ask` | User said stop | Never ask for more context |

## Key Principles

- **No config keys visible** — use natural language sections, not "topics: [array]"
- **Learn from behavior** — if they skip sports stories, note in Exclusions
- **Most users stay `ongoing`** — always learning new preferences, that's fine
- Update `last` on each briefing delivery
- Interests/Exclusions evolve over time — old entries can be removed if outdated
