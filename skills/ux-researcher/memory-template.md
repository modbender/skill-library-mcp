# Memory Template — UX Researcher

Create `~/ux-researcher/memory.md` with this structure:

```markdown
# UX Researcher Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Products Researched
<!-- List of products/projects analyzed -->

## Preferences
<!-- Output format preferences, focus areas -->

## Key Patterns Learned
<!-- Insights that apply across projects -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning |
|-------|---------|
| `ongoing` | Learning their context |
| `complete` | Knows their products and preferences |
| `paused` | Not actively researching |

## Research Output Structure

For each product researched, create `~/ux-researcher/research/{product}/`:

### personas.md
```markdown
# User Personas: {Product}

## Primary Persona: {Name}
**Role:** ...
**Goal:** ...
**Frustration:** ...

[Full persona details per SKILL.md template]

## Secondary Persona: {Name}
...

## Anti-Persona: {Name}
Who this product is NOT for...
```

### pain-points.md
```markdown
# Pain Points: {Product}

## Critical
[High frequency + high severity issues]

## Significant
[Medium priority issues]

## Minor
[Lower priority issues]
```

### journey-map.md
```markdown
# User Journey: {Product}

## Awareness
...

## Consideration
...

## First Use
...

## Regular Use
...

## Advocacy/Churn
...
```

### recommendations.md
```markdown
# UX Recommendations: {Product}

## Quick Wins
[Low effort, high impact]

## Strategic Improvements
[Higher effort, high impact]

## Nice-to-Haves
[Lower priority]
```
