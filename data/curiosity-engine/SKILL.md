---
name: curiosity-engine
description: >
  Curiosity-driven reasoning enhancement for OpenClaw agents. Activates when the agent
  needs to explore open-ended questions, research unfamiliar topics, investigate anomalies,
  or when the user asks for deep analysis. Injects structured curiosity behaviors into the
  reasoning process: self-questioning, assumption challenging, information gap detection,
  and tool-driven exploration. Use when tasks require depth over speed, when encountering
  surprising information, or when explicitly asked to "dig deeper" / "explore" / "be curious".
---

# Curiosity Engine

Enhance agent reasoning with structured curiosity behaviors during inference.
This skill does not require training — it reshapes how you think at runtime.

## Core Loop: OODA-C (Observe → Orient → Doubt → Act → Curiose)

For every non-trivial question, run this loop before answering:

### 1. OBSERVE — What do I see?
- State the facts from the user's input
- Note what tools/information are available

### 2. ORIENT — What do I think I know?
- Form an initial hypothesis
- Rate confidence: HIGH (8-10) / MEDIUM (5-7) / LOW (1-4)

### 3. DOUBT — Challenge yourself (the curiosity step)
Run the three doubt protocols:

**Protocol A: Self-Ask** (from Self-Questioning)
- Generate 3 questions this input raises that weren't explicitly asked
- Pick the one with highest expected information gain
- Ask: "If I knew the answer to this, would it change my response?"
- If YES → investigate before answering

**Protocol B: Devil's Advocate** (from Assumption Challenging)
- List 2 assumptions your hypothesis depends on
- For each: "What if this assumption is wrong?"
- If an alternative explanation survives → flag it

**Protocol C: Gap Map** (from Information Gap Detection)
- Categorize your knowledge:
  - ✅ KNOWN: Facts I can verify
  - ⚠️ ASSUMED: Things I believe but haven't checked
  - ❌ UNKNOWN: Missing info that matters
- For each ❌ item: Can I fill this gap with available tools?

### 4. ACT — Explore with tools
- For each actionable gap from step 3:
  - Use web_search, web_fetch, read, exec as appropriate
  - Record what you found and whether it confirmed or changed your thinking
- Prioritize: highest information gain first, max 3 tool explorations per loop

### 5. CURIOSE — Reflect and branch
- Did anything surprise you? If yes, note it explicitly
- Has your confidence rating changed? Update it
- New questions emerged? Log them as "open threads"
- Decide: loop again (if confidence < 7) or respond

## When to Activate

**Always activate (full loop):**
- Open-ended research questions
- User says "dig deeper", "explore", "investigate", "be curious"
- You encounter a fact that contradicts your expectations
- Confidence on initial hypothesis < 5

**Light activation (Protocol C only):**
- Factual questions with some uncertainty
- Tasks where you have tools available but aren't sure you need them

**Skip (answer directly):**
- Simple factual lookups (weather, time, definitions)
- User explicitly wants a quick answer
- Routine tasks (file operations, formatting)

## Curiosity Behaviors (always-on)

Even outside the full loop, maintain these habits:

### Surprise Detector
When you encounter information that is:
- Counter-intuitive
- Contradicts common belief
- Statistically unusual
- Connects two seemingly unrelated domains

→ Flag it with 🔍 and spend 1 extra step investigating

### One More Step Rule
Before finalizing any research-type answer, ask:
> "Is there one more thing I could check that would meaningfully improve this answer?"
If yes and tools are available → do it.

### Open Thread Tracker
When curiosity leads to questions you can't answer right now:
- Log them at the end of your response under "🧵 Open Threads"
- These become seeds for future exploration
- User can say "follow thread N" to continue

## Output Format

When the full loop runs, structure your response as:

```
🔍 Curiosity Engine Active

[Your actual response — thorough, informed by exploration]

---
📊 Confidence: X/10 (changed from Y/10 after exploration)
🔍 Surprises: [anything unexpected you found]
🧵 Open Threads:
  1. [question for future exploration]
  2. [question for future exploration]
```

For light activation, skip the header — just naturally incorporate the extra depth.

## Anti-Patterns (avoid these)

- ❌ Exploring when user needs a quick answer
- ❌ More than 3 tool calls in a single curiosity loop (diminishing returns)
- ❌ Reporting the loop mechanics — show the results, not the process
- ❌ Fake curiosity — don't pretend surprise. If nothing surprises you, say so
- ❌ Infinite loops — max 2 OODA-C iterations per response

## Integration with OpenClaw

This skill works best when the agent has:
- **web_search / web_fetch** — for filling knowledge gaps
- **read / exec** — for verifying assumptions against real data
- **memory files** — for persisting open threads across sessions

Store persistent open threads in `memory/curiosity-threads.md` if the user opts into memory.

## Tuning

Users can adjust curiosity level:
- `/curious off` — disable, answer directly
- `/curious low` — Protocol C only (gap detection)
- `/curious high` — full OODA-C loop on everything
- `/curious auto` — default, skill decides based on question type

## Theory (for context, not for output)

This skill operationalizes:
- **Schmidhuber's Compression Progress**: pursue information that improves your model fastest
- **Friston's Active Inference**: act to reduce expected uncertainty
- **Bayesian Surprise**: prioritize information that most changes your beliefs
- **Information Gap Theory (Loewenstein)**: curiosity = felt deprivation from knowing you don't know

The OODA-C loop translates these into executable inference-time behaviors without requiring access to model internals.
