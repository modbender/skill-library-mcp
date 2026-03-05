# Memory Template — Matomo Analytics

Create `~/matomo/memory.md` with this structure:

```markdown
# Matomo Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Sites
<!-- Add as you learn them -->
| Name | idSite | Purpose | Default |
|------|--------|---------|---------|
| Example | 1 | Main website | ✓ |

## Connection
matomo_url: (URL when provided)
token_ref: (keychain/env reference, never actual token)

## Priorities
<!-- What metrics matter to them -->
- Primary: (e.g., conversion rate)
- Secondary: (e.g., traffic sources)

## Preferences
<!-- How they like data presented -->
- Comparison period: vs last week | vs last month | vs last year
- Number format: exact | abbreviated (K/M)

## Notes
<!-- Observations from conversations -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning their setup | Gather context |
| `complete` | Have sites + connection + priorities | Work normally |
| `paused` | User said "not now" | Don't ask, use what you have |

## Directory Structure

```
~/matomo/
├── memory.md         # This file
├── reports/          # Saved report templates
│   └── weekly.md     # Example: weekly summary template
└── queries/          # Reusable API patterns
    └── common.md     # Frequently used queries
```

## Report Template Example

`~/matomo/reports/weekly.md`:
```markdown
# Weekly Report Template

## Queries
- VisitsSummary.get period=week date=lastWeek
- Actions.getPageUrls period=week date=lastWeek
- Referrers.getWebsites period=week date=lastWeek

## Format
1. Headline metrics vs previous week
2. Top 5 pages
3. Top 3 traffic sources
4. Notable changes (>10% delta)
```
