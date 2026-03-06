---
name: auto-doc-index
description: "Auto-generate document index tables (ADR, RFC, Pitfall, etc.) from file frontmatter. In real-world testing, hand-maintained indexes had a 62% error rate — titles truncated, statuses fabricated, dates invented. This skill eliminates that silent drift. Use when creating doc directories, adding ADRs/RFCs, or setting up documentation governance."
---

# Auto Doc Index — Derived Indexes from Frontmatter

Replaces hand-maintained index tables in `README.md` with auto-generated
tables derived from structured frontmatter in individual doc files.

## Why This Matters — Real Evidence

In a real project with 13 ADR files, comparing hand-maintained index vs
auto-generated index revealed **8 discrepancies (62% error rate)**:

| Issue Type | Example | Count |
|------------|---------|-------|
| **Title truncated** | "activate none" vs actual "activate none **by default**" | 2 |
| **Status fabricated** | Index said "Decided" but file said "Accepted" | 3 |
| **Date invented** | Index showed "2026-01-28" but file had no Date field | 1 |
| **Metadata lost** | "(revised 2026-01-28)" stripped from status | 1 |
| **Case "normalized"** | `decided` silently changed to `Decided` | 4 |

These aren't hypothetical risks — they were **already present and invisible**
in a well-maintained project. Hand-editing creates a false sense of
correctness while the index silently diverges from its source files.

## When to Use

- Setting up a new documentation directory (ADR, RFC, Pitfall, Design Doc, etc.)
- Adding a new document to an existing indexed directory
- Onboarding a project that has hand-maintained doc indexes showing signs of drift
- Resolving recurring merge conflicts in shared `README.md` index tables
- Migrating from hand-maintained indexes to auto-generated ones

## Boundaries

- This skill generates **index tables only** — it does not create or modify the content of individual documents.
- The generator script replaces content **only between `<!-- INDEX:START -->` and `<!-- INDEX:END -->` markers**. All other README.md content is preserved verbatim.
- Do NOT use this for indexes that require editorial curation (e.g., "recommended reading order"). Auto-generation is for factual, exhaustive catalogs.
- Do NOT introduce YAML frontmatter parsing libraries — the regex-based approach is intentional to keep the script zero-dependency.
- This skill targets file-system-based documentation. It does not apply to wiki-style or database-backed doc systems.

## Problem

A hand-maintained index in `README.md` is **shared mutable state** — every
new document requires editing the same file, same table, often the same diff
hunk. In multi-agent or multi-contributor workflows this creates:

- **Silent data loss**: titles get shortened, statuses get "corrected"
- **Merge conflicts**: semantically independent changes collide in the same hunk
- **Stale indexes**: contributors forget to update, nobody notices
- **Normalization illusion**: edits look "cleaner" but diverge from source

## Solution

Each document is self-describing via frontmatter. A generator script scans
the directory, parses frontmatter, and injects the index table between
`<!-- INDEX:START -->` / `<!-- INDEX:END -->` markers in README.md.

**Write ops become N:N (each file independent). Index becomes a stateless pure function.**

## Setup Steps

### 1. Define frontmatter convention

Choose a frontmatter format for your doc type. Two common patterns:

**Pattern A — Inline metadata (ADR/RFC style):**
```markdown
# ADR-001: Title Here

Status: Decided
Date: 2026-01-28

## Context
...
```

**Pattern B — Bold-field metadata (Pitfall/Postmortem style):**
```markdown
# PIT-001: Title Here

**Date:** 2026-01-28
**Area:** engine
**Severity:** high
**Status:** resolved
```

### 2. Add markers to README.md

Wrap the existing index table (or create a placeholder) with markers:

```markdown
## Index

<!-- INDEX:START -->
| ADR | Title | Status | Date |
|-----|-------|--------|------|
<!-- INDEX:END -->

## Other Sections (preserved)
...
```

Content outside markers is **never touched** by the generator.

### 3. Create the generator script

Copy `template/generate-doc-index.ts` from this skill's template directory,
or generate a new one following the pattern below.

**Core architecture (zero external dependencies):**

```typescript
// 1. Scan directory for matching files (e.g. /^\d{3}-.*\.md$/)
// 2. Parse frontmatter from each file (regex-based, no YAML lib needed)
// 3. Sort entries by ID/number
// 4. Generate markdown table string
// 5. Inject between <!-- INDEX:START --> and <!-- INDEX:END --> markers
```

See [template/generate-doc-index.ts](template/generate-doc-index.ts) for a
working implementation that handles both Pattern A and Pattern B.

### 4. Run the generator

```bash
npx tsx scripts/generate-doc-index.ts all
```

### 5. Update documentation governance

Add to your project's AGENTS.md or CONTRIBUTING.md:

> **Rule**: Never hand-edit the index table between `<!-- INDEX:START/END -->`
> markers. To add a new document, create the `.md` file with proper
> frontmatter, then run the generator.

## Workflow Comparison

```
OLD: Write doc → Hand-edit README.md index → Conflict risk
NEW: Write doc → Run generator → Idempotent rebuild, zero conflicts
```

## Adding a New Doc Type

To support a new document category (e.g. RFCs, Design Docs):

1. Define the frontmatter convention
2. Add a parser function (regex for title, status, date, etc.)
3. Add a table generator function (column layout)
4. Add `<!-- INDEX:START/END -->` markers to the README.md
5. Register in the script's `main()` dispatcher

## Anti-patterns

- Do NOT use YAML frontmatter libraries — regex is sufficient and avoids deps.
- Do NOT generate the entire README.md — only the index section. Preserve
  manually-written intro, templates, and notes via the marker pattern.
- Do NOT require contributors to run the generator before committing.
  Run it in CI or as a pre-commit hook for enforcement.

## Checklist

```
- [ ] Frontmatter convention defined for each doc type
- [ ] README.md has <!-- INDEX:START --> and <!-- INDEX:END --> markers
- [ ] Generator script created and tested
- [ ] Documentation governance updated (AGENTS.md / CONTRIBUTING.md)
- [ ] (Optional) Pre-commit hook or CI step added
```
