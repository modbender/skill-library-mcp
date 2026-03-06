# Memory Template — Competitor Research

Create `~/competitor-research/memory.md` with this structure:

```markdown
# Competitor Research Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Context
<!-- User's situation, natural language -->
<!-- New market entry or existing business? -->
<!-- What decisions does research inform? -->

## Preferences
depth: standard | quick | deep
focus: all | specific areas
style: detailed reports | quick summaries

## Active Niches
<!-- Niches currently being researched -->
- niche-name: last researched YYYY-MM-DD, X competitors analyzed

## Notes
<!-- Observations, patterns noticed across research -->
<!-- Things to remember for future sessions -->

---
*Updated: YYYY-MM-DD*
```

## Niche Overview Template

Create `~/competitor-research/niches/{niche}/overview.md`:

```markdown
# {Niche} Competitive Landscape

## Market Overview
<!-- What is this market? Who are the customers? -->
<!-- Market size if known, growth trends -->

## Key Players
| Competitor | Segment | Differentiator | Notes |
|------------|---------|----------------|-------|
| Company A  | Enterprise | Security-first | Leader |
| Company B  | SMB     | Simplicity     | Growing fast |

## Positioning Map
<!-- How players position themselves -->
<!-- Who owns what space? -->

## Gaps Identified
- Gap 1: description
- Gap 2: description

## Opportunities
- Opportunity 1: why it exists, how to exploit
- Opportunity 2: description

## Research History
- YYYY-MM-DD: Initial landscape scan
- YYYY-MM-DD: Deep dive on Company X

---
*Last updated: YYYY-MM-DD*
```

## Competitor Profile Template

Create `~/competitor-research/niches/{niche}/{company}.md`:

```markdown
# {Company} — Competitor Profile

## Basics
- **What they do:** One sentence description
- **Target customer:** Who they sell to
- **Pricing:** Model and range
- **Founded:** Year
- **Size indicators:** Funding, employees, revenue if known
- **Website:** URL

## Product
### Core Features
- Feature 1
- Feature 2

### Differentiators
- What makes them unique

### Weaknesses
- Known gaps or complaints

### Recent Changes
- YYYY-MM-DD: Change observed

## Positioning
- **Headline:** Their main message
- **Value props:** Top 3
- **Tone:** How they communicate
- **Compare against:** Who they position vs

## Traction Signals
- **Reviews:** G2/Capterra scores
- **Social proof:** Customer logos, testimonials
- **Growth indicators:** What suggests growth

## Win/Lose Analysis
### Why customers choose them
- Reason 1
- Reason 2

### Why customers might choose us instead
- Reason 1
- Reason 2

## Sources
- Source 1: URL (YYYY-MM-DD)
- Source 2: URL (YYYY-MM-DD)

---
*Last updated: YYYY-MM-DD*
*Confidence: High/Medium/Low*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning context | Gather preferences opportunistically |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |

## Key Principles

- **No config keys visible** — use natural language, not "depth: quick"
- **Learn from behavior** — observe preferred depth, don't interrogate
- **Build over time** — each session adds to niche knowledge
- **Date everything** — research gets stale, dates matter
- Update `last` on each use
