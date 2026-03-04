# Memory Template — Genomics

Create `~/genomics/memory.md` with this structure:

```markdown
# Genomics Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context

**Role:** [bioinformatician | geneticist | clinician | researcher | mixed]

**Focus areas:**
- Organisms: 
- Disease areas: 
- Analysis types: [germline | somatic | both]

**Technical environment:**
- Reference genome: GRCh38
- Compute: [local | HPC | cloud]
- Primary tools: 

## Preferences

**Annotation sources prioritized:**
- 

**Filtering defaults:**
- MAF threshold: 
- Quality filters: 

**Reporting style:**
- 

## Active Projects

<!-- Track ongoing analyses -->

| Project | Type | Status | Notes |
|---------|------|--------|-------|
| | | | |

## Notes

<!-- Observations, learned preferences, things to remember -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning their workflow | Gather context opportunistically |
| `complete` | Knows their full setup | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |

## Key Principles

- No config keys visible to user — natural language only
- Learn from their questions and corrections
- Update preferences when they mention changes
- Track active projects so context carries across sessions
- Most users stay `ongoing` — workflows evolve
