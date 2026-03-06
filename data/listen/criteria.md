# Criteria for Transcription Corrections

Reference only — consult when deciding whether to add a correction.

## When to Add

**Immediate (1 occurrence):**
- User explicitly corrects: "I said X, not Y"
- User re-says something after confusion
- Proper noun clearly garbled

**After pattern (2+ occurrences):**
- Same word transcribed wrong multiple times
- Similar-sounding errors repeat

## When NOT to Add
- User misspoke (not transcription error)
- Ambiguous homophones in context
- One-off unclear audio

## Confidence Levels

- `(?)` — Single occurrence, uncertain
- `(likely)` — 2-3 occurrences  
- `(confirmed)` — User explicitly confirmed or 4+ occurrences

## How to Write Entries

**Ultra-compact:**

Corrections examples:
- `claw → Claw (confirmed)`
- `alpha bravo → Alpha Bravo (likely)`
- `next js → Next.js (?)`

Patterns examples:
- `brand names get lowercased`
- `technical terms split into words`
- `Spanish names anglicized`

Context examples:
- `Kubernetes`
- `PostgreSQL`
- `company-specific: Widenex`

Never examples:
- `their/there/they're — context-dependent`
- `to/too/two — ignore`

## Proactive Validation

When to ask before proceeding:
- Word doesn't fit context
- Name seems garbled
- Technical term misspelled in audio-typical way

Ask: "Did you mean [X]? This often gets transcribed as [Y]"

## Maintenance
- Keep SKILL.md under 35 lines
- Merge similar corrections
- Promote (?) → (likely) → (confirmed) as evidence grows
