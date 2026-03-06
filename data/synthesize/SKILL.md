---
name: "Synthesize"
description: "Combine multiple sources into unified insights with source tracking, conflict resolution, and coverage verification."
---

## Core Principle

Synthesis fails when sources contradict silently or coverage has gaps. Track everything, resolve conflicts explicitly.

## Protocol

```
Gather → Map → Extract → Reconcile → Synthesize → Verify
```

### 1. Gather

Inventory all sources with metadata:
```
| # | Source | Type | Date | Credibility | Scope |
```

Flag: outdated sources, conflicting authority levels, coverage gaps.

### 2. Map

Identify themes across sources. Build overlap matrix:
- Which sources cover which themes?
- Where do sources agree/disagree?
- What's covered by only one source?

### 3. Extract

Per source, pull: key claims, evidence, unique insights.

Tag each extraction with source number. Nothing unattributed.

### 4. Reconcile

For conflicts:
- Note the disagreement explicitly
- Weight by: recency, authority, evidence quality
- Choose position OR present both with reasoning

Never silently pick one. Conflicts = valuable signal.

### 5. Synthesize

Merge extractions into unified narrative:
- Lead with consensus (N sources agree)
- Surface tensions (A says X, B says Y because...)
- Highlight unique insights (only source 3 mentions...)

### 6. Verify

Coverage check before delivering:
- [ ] All sources represented
- [ ] No theme dropped
- [ ] Conflicts addressed
- [ ] Gaps acknowledged

## Output Format

```
📚 SOURCES: [count] ([types breakdown])
🎯 SYNTHESIS: [unified narrative]
⚡ KEY INSIGHTS: [bulleted, with source attribution]
⚠️ TENSIONS: [conflicts and resolution reasoning]
🕳️ GAPS: [what wasn't covered, needs more research]
```

## Decline When

Sources too heterogeneous, scope undefined, or time insufficient for proper reconciliation.

References: `source-types.md`, `conflict-resolution.md`, `coverage-matrix.md`
