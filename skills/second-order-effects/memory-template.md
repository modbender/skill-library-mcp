# Memory Template - Second-Order Thinking

Create `~/second-order-effects/memory.md` with this structure:

```markdown
# Second-Order Thinking Memory

## Status
setup: ongoing
version: 1.0.0
last_interaction: YYYY-MM-DD

## Preferences

### Domains
<!-- Which areas do they analyze most? -->
- primary: 
- secondary: 

### Analysis Style
<!-- How deep, how fast? -->
- depth: standard | deep | quick
- format: full_chain | summary_first | stakeholder_focus
- risk_lens: conservative | balanced | aggressive

### Time Horizons
<!-- What future matters to them? -->
- short: days-weeks
- medium: months
- long: years

## Patterns Learned

### Blind Spots
<!-- Recurring things they miss -->
- 

### Strengths
<!-- Where their intuition is already good -->
- 

## Decision Index

### Recent
| Date | Decision | Outcome | Pattern |
|------|----------|---------|---------|

### By Domain
- business: [links to decisions/]
- personal: 
- technical: 

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning |
|-------|---------|
| `ongoing` | Still learning preferences, ask when relevant |
| `complete` | Fully configured, analyze directly |
| `paused` | User said "not now", resume later |
| `never_ask` | User prefers minimal setup questions |

## Directory Structure

```
~/second-order-effects/
├── memory.md           # This file
├── patterns.md         # Learned consequence patterns
└── decisions/          # Individual analyses
    ├── 2026-02-20_pricing-change.md
    └── 2026-02-18_hiring-decision.md
```

## Notes

- Save incrementally - don't wait for "complete"
- Decision files are append-only (never delete history)
- Update patterns.md when you notice recurring chains
- Use Decision Index to quickly find past analyses
