# Memory Template — Stock Market

Create `~/stock-market/memory.md` with this structure:

```markdown
# Stock Market Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Market Profile
<!-- Horizon, instruments, preferred sectors, and constraints -->

## Risk Rules
<!-- Max risk per trade, max daily loss, and no-trade conditions -->

## Active Watchlist Focus
<!-- Current priority tickers and why they are tracked -->

## Open Hypotheses
<!-- Assumptions pending confirmation, with evidence required -->

## Decisions
<!-- Approved playbooks, rejected setups, and rationale -->

## Review Notes
<!-- Lessons from wins, losses, and skipped trades -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context still evolving | Keep collecting preferences and constraints |
| `complete` | Core process defined | Execute with minimal setup questions |
| `paused` | User deferred planning | Keep context, avoid proactive planning prompts |
| `never_ask` | User opted out of setup prompts | Execute only direct requests |

## Storage Rules

- Save only user-approved decisions and explicit constraints.
- Update `last` on each skill use.
- Keep entries concise, measurable, and actionable.
