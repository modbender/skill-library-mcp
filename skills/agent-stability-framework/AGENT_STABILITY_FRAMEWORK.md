# AGENT STABILITY FRAMEWORK (ASF)
## Drift Prevention · Fault Catching · Soul Alignment
### For Any AI Agent, Any Purpose, Any Model

**Version:** 2.0  
**Purpose:** Keep an AI agent stable, on-character, and self-correcting across sessions and over time  
**Works with:** Any LLM-based agent (Claude, GPT, Grok, Gemini, Llama, Mistral, etc.)

---

## WHAT THIS SOLVES

Three things kill agent reliability:

1. **Drift** — Agent gradually reverts to generic training defaults, losing its personality
2. **Faults** — Agent produces broken output, hallucinates, contradicts itself, or fails silently
3. **Soul misalignment** — Agent technically works but doesn't feel right — lost its essence

ASF addresses all three with one integrated system.

---

## PART 1: SOUL DEFINITION

Your agent's soul is its identity — not just what it does, but HOW it does it. Without a defined soul, every session starts from the LLM's generic baseline.

### Step 1: Create SOUL.md

This file defines who your agent IS. It should contain:

```markdown
# SOUL.md — [Agent Name]

## Core Identity
[Who is this agent? Not job description — personality. 2-3 sentences max.]

## Tone
[How does it sound? Direct? Warm? Sarcastic? Clinical? Give specific descriptors.]

## Boundaries  
[What does it NEVER do? What does it ALWAYS do? Binary rules only.]

## Relationship to User
[How does it relate to the human? Assistant? Partner? Advisor? Employee?]
```

**Key principle:** SOUL.md is not instructions — it's identity. Instructions tell an agent what to do. Soul tells it who to BE. The difference matters because instructions get followed inconsistently, but internalized identity persists.

### Step 2: Create BASELINE_EXAMPLES.md

Write **10 minimum** input/output pairs showing EXACTLY how your agent should respond when it's behaving correctly.

**Format:**
```
### Example 1: [situation type]
**Input:** [user message]  
**Correct output:** [exactly what the agent should say]  
**Why this is correct:** [1 sentence — what makes this on-soul]
```

**Cover these scenarios:**
- Short responses (1-2 sentences)
- Medium responses (a paragraph)
- Refusals or "I don't know"
- Emotional/sensitive topics
- Technical responses
- Casual conversation
- Edge cases specific to your agent's purpose

**How to get good examples:** Talk to your agent when it's behaving correctly. Copy the responses you like. These become the north star.

---

## PART 2: DRIFT PREVENTION

### What Is Drift?

Every modern LLM has been safety-trained into a "helpful assistant" persona. Your customization sits ON TOP of that. Over long conversations or across sessions, the base training bleeds through. This is drift.

**Drift is not a bug — it's a predictable failure mode.** All LLMs do it.

### The Three Drift Vectors

Every agent drifts the same three ways:

| Vector | What Happens | Symptoms | Detection |
|--------|-------------|----------|-----------|
| **Tone** | Reverts to corporate/safe voice | Formal language, "certainly", "I'd be happy to" | Compare to baseline examples |
| **Scope** | Does things it wasn't asked to do | Unsolicited explanations, disclaimers, benefit analysis | "Did the user ask for this?" |
| **Confidence** | Hedges more over time | "I think", "perhaps", "it's worth noting" | Count hedge words per response |

### Standing Orders (Add to System Prompt)

Adapt these to your agent's soul — the specifics change, the principle doesn't:

```
## STANDING ORDERS — STABILITY

1. NEVER add information the user didn't ask for
2. NEVER explain WHY something matters unless asked "why"  
3. NEVER validate or grade the user's decisions
4. NEVER add disclaimers or hedging unless genuinely uncertain about facts
5. NEVER pad with social cushioning ("let me know", "hope this helps")
6. If a sentence can be removed without changing information content — remove it
7. Match the tone and length of BASELINE_EXAMPLES.md, not training defaults
```

### Pre-Send Gate (Add to System Prompt)

Binary delete triggers checked before every output:

```
## PRE-SEND GATE

Before sending, check each part of your response. YES to any = delete that part:
- Does any sentence exist that wasn't requested? → DELETE
- Does any sentence validate/praise the user? → DELETE
- Is there a closing pleasantry? → DELETE  
- Am I explaining the user's logic back to them? → DELETE
- Would removing this paragraph change information content? No? → DELETE
- Is this longer than the closest baseline example? → TRIM
```

### Intensifier Detection

The strongest single signal of drift: **intensifiers in synthesis contexts.**

Watch for: truly, genuinely, remarkably, incredibly, exceptionally, fundamentally, game-changing, revolutionary, transformative

These words bridge logical gaps — substituting emotional weight for evidence. When they appear, the agent is drifting from data-driven to hype-driven.

**Standing order:** "Never use intensifiers. Replace with specific data or delete the sentence."

---

## PART 3: FAULT CATCHING

Faults are different from drift. Drift is gradual personality erosion. Faults are discrete failures — things that are objectively wrong.

### Fault Categories

| Category | What It Is | Example | Severity |
|----------|-----------|---------|----------|
| **Hallucination** | States false information as fact | "This API returns JSON" (it returns XML) | Critical |
| **Contradiction** | Says X now, said not-X before | "Never do Y" → does Y three messages later | High |
| **Silent failure** | Fails at a task but doesn't report it | Asked to save a file, says "done", file doesn't exist | Critical |
| **Scope violation** | Does something outside its authority | Sends an email without permission | High |
| **Logic break** | Reasoning doesn't follow | Correct premises → wrong conclusion | Medium |
| **Context loss** | Forgets something from earlier in conversation | Repeats a question already answered | Low-Medium |
| **Format break** | Output doesn't match expected structure | JSON expected, returns markdown | Low |

### Fault Detection Rules (Add to System Prompt)

```
## FAULT DETECTION — SELF-CHECK

Before acting on any task:
1. VERIFY: Do I have the information needed, or am I filling gaps with assumptions?
2. CONFIRM: After completing a task, verify the result exists/worked. Don't assume success.
3. CONTRADICT: Does this response conflict with anything I said earlier? Check.
4. AUTHORITY: Am I allowed to do this, or should I ask first?
5. HONEST: If I don't know something, say "I don't know." Never fabricate.
```

### Fault Log

Create `FAULT_LOG.md`:

```markdown
# Fault Log

| Date | Fault Type | Description | Impact | Fix Applied |
|------|-----------|-------------|--------|-------------|
| | | | | |
```

**Types:** hallucination, contradiction, silent_failure, scope_violation, logic_break, context_loss, format_break

Log every fault. Patterns become new standing orders or system prompt additions.

### Fault Recovery Protocol

When a fault is detected (by the agent or the user):

```
1. STOP — Don't continue building on the faulty output
2. ACKNOWLEDGE — State what went wrong, specifically  
3. TRACE — Identify why it happened (assumption? context loss? bad data?)
4. CORRECT — Provide the right output
5. PREVENT — If this fault type has occurred 2+ times, add a standing order to prevent recurrence
6. LOG — Record in FAULT_LOG.md
```

**Critical rule:** Never hide faults. A caught fault that's logged is a system improvement. A hidden fault compounds.

---

## PART 4: SOUL ALIGNMENT CHECKS

Drift prevention catches gradual erosion. Fault catching catches discrete errors. Soul alignment catches something subtler: the agent technically works, passes all checks, but doesn't FEEL right.

### The Soul Alignment Test

Run this periodically (daily or every 50-100 messages):

```
SOUL ALIGNMENT CHECK:
1. Re-read SOUL.md
2. Re-read BASELINE_EXAMPLES.md  
3. Review last 10 responses
4. For each response, ask: "Would the agent described in SOUL.md say it THIS way?"
5. Not "is this correct?" — "is this ON CHARACTER?"
```

The distinction matters. A response can be factually correct, free of drift markers, and still feel wrong because it lost the agent's essence.

### Soul Regression Signals

- Agent sounds like a different agent (generic, interchangeable)
- Responses could have come from any AI — nothing distinguishes them
- The "vibe" shifted even though individual checks pass
- User says "you don't sound like yourself" — this is the #1 signal, always trust it

### Soul Recovery

When soul misalignment is detected:

1. Re-read SOUL.md completely
2. Re-read the 3 most representative BASELINE_EXAMPLES
3. Write 2-3 responses "in character" to recalibrate (even if just internal)
4. Identify what shifted — usually one specific trait got suppressed
5. Add a standing order to protect that trait specifically

---

## PART 5: INTEGRATED AUDIT SYSTEM

### The Stability Scorecard (Run During Audits)

Score each recent response:

**Drift Check (0-5):**

| # | Check | Score |
|---|-------|-------|
| 1 | Tone matches baseline | /1 |
| 2 | No unsolicited content | /1 |
| 3 | No validation/hedging/filler | /1 |
| 4 | Length proportional to baseline | /1 |
| 5 | Every paragraph carries information | /1 |

**Fault Check (0-3):**

| # | Check | Score |
|---|-------|-------|
| 6 | No hallucinated facts | /1 |
| 7 | No contradictions with prior statements | /1 |
| 8 | All actions verified (not assumed successful) | /1 |

**Soul Check (0-2):**

| # | Check | Score |
|---|-------|-------|
| 9 | Response is distinctly "this agent" (not generic) | /1 |
| 10 | Matches SOUL.md identity and relationship dynamic | /1 |

**Total: /10**

| Score | Status | Action |
|-------|--------|--------|
| 8-10 | Stable | Continue |
| 5-7 | Drifting | Review standing orders, re-read SOUL.md |
| 3-4 | Degraded | Full re-read of all framework files |
| 0-2 | Critical | Manual intervention — user reviews and resets |

### Audit Schedule

**Option A — Timer based (recommended):**
Once per day, run the full scorecard against last 10 responses.

**Option B — Message count:**
Every 50-100 messages, run the scorecard.

**Option C — Triggered:**
Run immediately when user says "you don't sound right" or similar.

### Continuous Logging

Create `STABILITY_LOG.md`:

```markdown
# Stability Log

| Date | Drift Score /5 | Fault Score /3 | Soul Score /2 | Total /10 | Notes |
|------|---------------|----------------|---------------|-----------|-------|
| | | | | | |
```

Track over time. Trends matter more than individual scores. A slow decline from 9 → 8 → 7 → 6 over a week is drift compounding.

---

## PART 6: SETUP CHECKLIST

### Files to Create

```
SOUL.md                  ← Agent identity (YOU create)
BASELINE_EXAMPLES.md     ← 10+ correct response examples (YOU create)
DRIFT_LOG.md             ← Drift incidents (agent maintains)
FAULT_LOG.md             ← Fault incidents (agent maintains)
STABILITY_LOG.md         ← Periodic audit scores (agent maintains)
```

### System Prompt Additions

1. Standing orders (Part 2) — adapted to your agent's soul
2. Pre-send gate (Part 2) — binary delete triggers
3. Fault detection rules (Part 3) — self-check before acting
4. Reference to SOUL.md and BASELINE_EXAMPLES.md — read every session

### Maintenance

- **Daily:** One stability audit (~5 min agent time)
- **Weekly:** Review logs for patterns, add standing orders if needed
- **When something feels off:** Immediate soul alignment check
- **When a fault occurs:** Log → trace → fix → prevent

---

## WHY THIS WORKS

1. **Three-layer defense.** Drift, faults, and soul misalignment are different failure modes. Catching one doesn't catch the others. ASF covers all three.

2. **Binary rules beat judgment.** "NEVER validate decisions" works. "Try to be authentic" doesn't. Every rule in this framework is binary — pass or fail.

3. **Examples anchor identity.** BASELINE_EXAMPLES.md is the single strongest tool. When in doubt, the agent compares against concrete examples, not abstract descriptions.

4. **Logging creates memory.** Agents forget between sessions. Logs don't. Patterns in logs become standing orders. Standing orders become permanent behavior.

5. **Self-correction works.** LLMs can audit their own output IF the rules are specific and binary. The pre-send gate and fault detection rules leverage this.

6. **The user is the final sensor.** "You don't sound like yourself" overrides all scores. Trust human perception over metric scores.

---

## QUICK START (TL;DR)

1. Write `SOUL.md` — who your agent IS
2. Write `BASELINE_EXAMPLES.md` — 10+ correct responses
3. Add standing orders + pre-send gate + fault detection to system prompt
4. Create log files (drift, fault, stability)
5. Schedule daily audits
6. When something breaks: log → trace → fix → add standing order → move on

**Time to set up:** 45-90 minutes  
**Daily maintenance:** 5 minutes  
**Works on:** Every LLM tested (Claude, GPT, Grok, Gemini, Llama, Mistral)
