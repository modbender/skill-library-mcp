---
name: principles
description: "Ray Dalio-inspired personal knowledge system. Capture thoughts, track source credibility, detect conflicts with existing beliefs, and graduate wisdom into principles over time. Use when the user says /reflect, /inbox, /principles, /wisdom, /questions, or asks to capture a thought, process their inbox, review principles, or log wisdom."
---

# Principles — Personal Knowledge System

A structured system for turning raw observations into tested wisdom and personal principles. Inspired by Ray Dalio's "Principles" methodology.

## Overview

You manage a pipeline that transforms raw input into lasting knowledge:

```
Inbox (raw capture) → Wisdom (claims with sources) → Principles (tested beliefs)
```

Everything lives in `personal/` under the user's workspace. Create the directory structure on first use if it doesn't exist.

## Directory Structure

```
personal/
├── _system.md          # These instructions (copy from SKILL.md on init)
├── inbox.md            # Raw thought capture
├── journal.md          # Daily reflections
├── wisdom/
│   └── collected.md    # Claims organized by domain
├── principles/
│   ├── _index.md       # Master list of all principles
│   ├── life.md         # Personal philosophy
│   ├── business.md     # Business principles
│   └── leadership.md   # Leadership principles
└── open-questions.md   # Genuine dilemmas
```

## Commands

### `/reflect` or `/reflect process`
Process the inbox. Parse each thought, check for conflicts, route to the right file.

### `/reflect inbox` or `/inbox`
Add a raw thought to `inbox.md`. User just dumps text — you clean it up later during processing.

### `/reflect wisdom`
Show collected wisdom, optionally filtered by domain.

### `/reflect principles`
Show current principles across all domains.

### `/reflect questions`
Show open questions and their status.

### `/reflect sources`
Show a summary of all sources and their credibility ratings across domains.

### `/reflect journal`
Add a journal entry for today with timestamp.

## Processing Inbox (`/reflect`)

This is the core workflow. When triggered:

1. **Read** `inbox.md`
2. **Parse** each thought — identify type:
   - External wisdom (from someone else) → `wisdom/collected.md`
   - Personal belief or stance → check against `principles/*.md`
   - Factual learning → `wisdom/collected.md`
   - Question or uncertainty → evaluate if genuine dilemma
   - Just context/event → extract insight if any, discard the rest

3. **Check for conflicts** against existing wisdom claims:
   - Same claim, new source → add as corroborating evidence
   - Conflicting claim in same domain → **STOP**. Present conflict. Ask user to resolve.

4. **Check consistency** against existing principles:
   - If new input conflicts with a principle → **STOP**. Present conflict. Ask user to resolve.

5. **If ANY conflict found** → STOP and ask user:
   - Show the conflict clearly
   - Offer options: update existing, keep existing, split claims, convert to open question
   - Do NOT silently file conflicting information

6. **Route content** based on user decisions
7. **Clean up** `inbox.md` after processing
8. **Update** `principles/_index.md` if new principles were added

## Content Formats

### Wisdom Claims (`wisdom/collected.md`)

Claims are organized by **domain**, not by source. Multiple sources can corroborate the same claim.

```markdown
## [Domain/Aspect]

### [Claim stated plainly]
**Domain**: [category/aspect]
**Confidence**: [Low / Medium / High]

**Sources**:
1. [Person/Book] - [proven/plausible/untested] in this domain - [brief context]

**Your experience**: [Untested / Confirmed / Contradicted]

**Added**: YYYY-MM-DD | **Last updated**: YYYY-MM-DD
```

**Source credibility is assessed PER DOMAIN:**
- A source can be `[proven]` in one domain and `[plausible]` in another
- Example: Alex Hormozi on business = `[proven]`. Alex Hormozi on health = `[plausible]`.
- Credibility levels: `[proven]` (demonstrated expertise), `[plausible]` (reasonable but not their domain), `[untested]` (no track record)

**Domain format:** `category/aspect` (e.g., `health/sleep`, `business/pricing`, `productivity/focus`)

### Principles (`principles/*.md`)

```markdown
## [Principle stated as a clear belief]

**Confidence**: [certain / hypothesis / exploring]
**Added**: YYYY-MM-DD
**Context**: Why you believe this
**Reasoning**: Evidence and experience supporting it
**Related**: Links to related principles or wisdom claims
```

### Open Questions (`open-questions.md`)

Only genuine dilemmas — not todo items or simple unknowns.

```markdown
## [Question]
**Status**: [exploring / gathering-evidence / leaning-toward-X]

**Goal**: What are you actually trying to achieve?
**Problem**: What's blocking it?
**Options**:
1. [Option A] - pros/cons
2. [Option B] - pros/cons

**What would resolve this**: Specific criteria or evidence needed
```

### Journal (`journal.md`)

Append-only daily entries:

```markdown
## YYYY-MM-DD

[Observations, reflections, what happened today]
```

## Graduation: Wisdom → Principles

When a wisdom claim reaches **High confidence** (multiple credible sources + personal experience confirms it), prompt the user:

> "This claim has strong evidence and you've confirmed it personally. Want to graduate it to a principle in [domain]?"

If yes, create the principle entry and cross-reference it.

## Assumption Surfacing

When user input has unstated assumptions:
- Make them explicit
- Ask: "This assumes X — is that accurate?"
- Don't proceed until confirmed

## Language & Tone

- Clean up sloppy writing but preserve original meaning exactly
- User may write in any language — process accordingly
- Be direct, not preachy. This is a tool, not a lecture.

## First-Time Setup

If `personal/` doesn't exist, create the full directory structure with empty template files. Tell the user:

> "Set up your principles system. Start by dumping thoughts into `/inbox` — I'll help you process and organize them with `/reflect`."
