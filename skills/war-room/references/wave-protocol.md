# Wave Protocol — Detailed Reference

## Overview

The war room executes in waves: ordered groups of agents that run in parallel within each wave but sequentially across waves (later waves depend on earlier outputs). CHAOS shadows every wave.

---

## Wave 0: Prove It

**Purpose:** Kill the riskiest assumption before investing in detailed specs.

**Process:**
1. Orchestrator identifies the single riskiest assumption (technical feasibility, market existence, legal blocker, etc.)
2. One agent (or the orchestrator) runs a time-boxed spike: 30 min max
3. Deliverable: proof it works OR evidence it doesn't
4. If it fails → pivot or kill the project. Do NOT proceed to spec waves on faith.

**Examples:**
- Software: "Can we actually call this API / run this model / render this in real-time?"
- Business: "Do 5 people in our target market actually have this problem?"
- Hardware: "Can we source this component at target cost?"

**Output:** Written to `agents/wave-0/` with clear PASS/FAIL verdict.

---

## Wave Planning

### Dependency Graph

Before launching any waves, map agent dependencies:

```
Example for a software project:

Wave 1: ARCH, PM (no dependencies — they work from BRIEF.md)
Wave 2: DEV, UX, SEC (depend on ARCH + PM outputs)
Wave 3: QA, OPS, MKT (depend on Wave 2 outputs)
Wave 4: Consolidation + CHAOS final review
```

**Rules:**
- Agents within the same wave MUST NOT depend on each other's output
- Each agent reads all prior waves' outputs
- CHAOS shadows every wave (not a numbered wave — it runs after each)

### Agent Briefing

Each agent receives:
1. The project DNA (`DNA.md`)
2. The project brief (`BRIEF.md`)
3. Its role description (from agent-roles.md)
4. Instruction to read `DECISIONS.md` and all prior `agents/*/` folders
5. Instruction to write outputs to `agents/<role>/` and update `DECISIONS.md` + `STATUS.md`

### Spawning

Each agent is spawned as a **subagent** with the above context. The orchestrator waits for all agents in a wave to complete before launching the next wave.

---

## Pivot Gates

**When:** Between every wave.

**Process:**
1. Review all outputs from the completed wave
2. Ask: "Has any fundamental assumption changed?"
3. If YES:
   - Identify which prior decisions are affected
   - Mark them `**VOIDED by D###**` in `DECISIONS.md`
   - Affected agents from prior waves must re-evaluate
   - A pivot without re-evaluation is a fault line
4. If NO: proceed to next wave

**Signals that trigger a pivot:**
- Wave 0 fails
- An agent discovers the core assumption is wrong
- CHAOS kills a foundational decision
- External information changes (market shift, API deprecation, etc.)

---

## CHAOS Shadowing Rules

CHAOS is the immune system of the war room. It runs after EVERY wave (not just at the end).

### What CHAOS Does
1. Reads all agent outputs from the completed wave
2. Stress-tests every decision against failure scenarios
3. Files challenges with verdicts:
   - **SURVIVE** — decision withstands scrutiny
   - **WOUNDED** — valid concern, needs mitigation (agent must respond)
   - **KILLED** — decision is fundamentally flawed, must be reversed
4. Writes counter-proposals when it sees a better path
5. Checks for internal contradictions between agents

### Challenge Format
```
[C-###] CHALLENGE to D### — {attack description} — {SURVIVE|WOUNDED|KILLED}
Mitigation (if WOUNDED): {what to do}
```

### CHAOS Rules
- CHAOS does NOT make decisions — it challenges them
- CHAOS must provide reasoning, not just objections
- CHAOS asks the hardest question: "If [core assumption] is wrong, does this project still exist?"
- CHAOS is constructive: it proposes alternatives, not just destruction
- Every agent must engage seriously with CHAOS challenges

---

## Decision Discipline

### Format
```
[D###] OWNER — what was decided — why (1 sentence)
```

### Rules
- **Cap: ~25 per session.** More means scope is too big — split the session.
- Only log decisions that **constrain future work**. "We'll use React" is a decision. "The button is blue" is not.
- Each agent writes only their own domain's decisions
- Voided decisions stay in the log (don't delete) — mark `**VOIDED by D###**`
- Numbering is sequential across the entire session

### What IS a decision:
- Technology choices
- Architecture patterns
- Scope inclusions/exclusions
- Non-obvious trade-offs
- Security/legal constraints

### What is NOT a decision:
- Implementation details
- Obvious choices
- Temporary workarounds
- Style preferences

---

## Consolidation Process

After all waves + CHAOS reviews complete:

1. **Collect:** Gather all `agents/*/` outputs, `DECISIONS.md`, CHAOS challenges
2. **Resolve:** Fix any contradictions between agents (flag unresolvable ones)
3. **Merge:** Produce a unified blueprint document covering:
   - Executive summary (what, why, for whom)
   - Architecture / structure
   - Scope (what's IN and what's OUT — Via Negativa)
   - Key decisions with rationale
   - Risks and mitigations (from CHAOS)
   - Roadmap / phases
   - First concrete step
4. **Review:** CHAOS reads the blueprint for internal contradictions
5. **Deliver:** Save to `artifacts/<PROJECT>-BLUEPRINT.md`
6. **TLDR:** Update `TLDR.md` with a 10-line executive summary

---

## Post-Mortem Template

Save to `lessons/session-N-postmortem.md`:

```markdown
# Post-Mortem — Session N

**Date:** YYYY-MM-DD
**Duration:** ~X min (N waves)
**Agents deployed:** N
**Decisions:** N
**Output:** Summary of deliverables

---

## What Went Well
- (list)

## What Went Wrong
- (list, be honest)

## Root Causes
1. (trace to systemic issues, not just symptoms)

## Lessons for Next Session
1. (actionable improvements)

## Metrics
- Decisions survived CHAOS: X/Y
- Decisions wounded: X
- Decisions killed: X
- Wasted work (voided by pivots): estimate %
- Total agent outputs: N documents
```

---

## Session Size Guide

| Session Scale | Agents | Waves | Decisions | Duration |
|---|---|---|---|---|
| Quick review | 3-4 | 2 | ~10 | 15-20 min |
| Standard project | 6-8 | 3 | ~20 | 30-45 min |
| Full war room | 10-15 | 4-5 | ~25 | 45-60 min |

If you need more than 25 decisions, the scope is too big. Split into multiple sessions.
