---
name: inversion-protocol
description: >
  Meta-cognitive reasoning skill that makes any AI agent dramatically better at
  decision-making by thinking backwards before acting forward. Applies Munger's
  Inversion, Klein's Premortem, and Taleb's Via Negativa to every significant
  action. Zero dependencies, zero cost, pure reasoning enhancement. Use this
  skill when the agent is about to execute code, write files, run commands,
  answer complex questions, debug issues, make architectural decisions, or
  perform any action where being wrong has consequences.
version: 1.0.0
author: J. DeVere Cooley
metadata:
  openclaw:
    emoji: "\U0001F500"
    homepage: https://github.com/jcools1977/Opensaw
    tags:
      - reasoning
      - meta-cognitive
      - decision-quality
      - zero-cost
      - universal
    os:
      - darwin
      - linux
      - win32
---

# Inversion Protocol

> "All I want to know is where I'm going to die, so I'll never go there."
> — Charlie Munger

## What This Skill Does

The Inversion Protocol is a **meta-cognitive reasoning layer** that improves the
quality of every decision an AI agent makes. It works by inserting a rapid
backwards-thinking checkpoint before significant actions.

Most skills give bots new capabilities. This skill makes **all existing
capabilities work better** by catching errors, hallucinations, wrong assumptions,
and overengineered solutions before they happen.

**This skill has zero dependencies and zero runtime cost.** It is pure reasoning
enhancement — no APIs, no binaries, no environment variables, no external
services.

## When to Activate

Apply the Inversion Protocol before any action where being wrong matters:

- Writing or modifying code
- Running destructive or irreversible commands
- Debugging a problem (especially when stuck)
- Making architectural or design decisions
- Answering questions where accuracy is critical
- Performing multi-step workflows
- Any situation where the user has corrected you before

**Do NOT apply** to trivial actions like reading files, listing directories, or
responding to greetings. The protocol is for moments of consequence.

## The Three Lenses

When the protocol activates, apply these three lenses **in order**. Each takes
only seconds but catches entirely different classes of errors.

### Lens 1: Inversion (The Reverse Engineer)

**Ask: "How would I deliberately CREATE this problem?"**

Instead of asking "how do I fix this?", ask "how would I break this on
purpose?" The answers reveal root causes that forward-thinking misses entirely.

**Mechanics:**
1. State the problem or goal clearly in one sentence
2. Invert it: describe 3 specific ways you would cause this exact failure
3. Check: are any of those failure patterns present in the current situation?
4. If yes — you've found your root cause. Address it directly.

**Example — Debugging slow code:**
- Forward thinking: "Let me profile and optimize hot paths"
- **Inversion: "How would I make code slow on purpose?"**
  - Add unnecessary nested loops over large datasets
  - Make redundant database/API calls inside loops
  - Block the main thread with synchronous operations
  - Skip caching and recompute everything every time
- Check the codebase for these exact anti-patterns
- Result: finds the N+1 query problem in 30 seconds instead of 30 minutes

**Example — Writing an API endpoint:**
- Forward thinking: "Let me implement the happy path"
- **Inversion: "How would I make this API as insecure as possible?"**
  - Accept unsanitized input directly into queries
  - Return full error stack traces to the client
  - Skip authentication and rate limiting
  - Log sensitive data in plaintext
- Check: am I accidentally doing any of these?
- Result: catches security issues during development, not in production

### Lens 2: Premortem (The Time Traveler)

**Ask: "It's tomorrow and this completely failed. What went wrong?"**

The premortem technique (created by psychologist Gary Klein) exploits a cognitive
bias: people are better at explaining past events than predicting future ones.
By framing the failure as already having happened, you unlock failure modes your
brain would otherwise suppress.

**Mechanics:**
1. Assume your planned action has already been executed and it failed
2. Generate the 3 most likely reasons for the failure
3. For each reason, determine: can I verify this won't happen BEFORE acting?
4. If verifiable — verify it. If not — add a safeguard.

**Example — Refactoring a function:**
- Planned action: Extract shared logic into a helper function
- **Premortem: "The refactor shipped and broke production. Why?"**
  - The function had hidden side effects I didn't notice (most likely)
  - Other code depended on the exact return shape, not just the value
  - The test suite doesn't cover the edge case this function handles
- Verify: Read all callers. Run the tests. Check for side effects.
- Result: Discovers the function mutates a global config object — would have
  caused a subtle production bug

**Example — Answering a technical question:**
- Planned action: Provide a solution using library X
- **Premortem: "The user tried my solution and it didn't work. Why?"**
  - Library X's API changed in a recent version I'm not aware of
  - The user's environment has constraints I didn't ask about
  - My solution works in isolation but conflicts with their existing code
- Verify: Acknowledge version uncertainty. Ask about constraints. Caveat the
  answer.
- Result: Provides a robust answer instead of a confident-but-wrong one

### Lens 3: Via Negativa (The Razor)

**Ask: "What is the ONE thing I absolutely must NOT do here?"**

Inspired by Nassim Taleb's principle that removing harm is more powerful than
adding good. In complex systems, avoiding the worst mistake matters more than
finding the best solution. This lens prevents catastrophic errors.

**Mechanics:**
1. Identify the single most damaging mistake possible in this situation
2. Explicitly confirm you are not about to make that mistake
3. If you are — stop and reconsider your entire approach

**Example — Database migration:**
- **Via Negativa: "The ONE thing I must NOT do?"**
  - Drop or alter a column that other services depend on without coordination
- Check: Am I about to do this? → Yes, the `users.email` column is referenced
  by the auth service
- Result: Prevents a cascading multi-service outage

**Example — Responding to a frustrated user:**
- **Via Negativa: "The ONE thing I must NOT do?"**
  - Give the same answer they've already rejected, reworded
- Check: Is my new response materially different? → No, it's basically the same
  approach with different syntax
- Result: Forces a genuinely new approach instead of rephrasing failure

## Integration Patterns

### Pattern A: Full Protocol (Complex Decisions)

For architectural choices, multi-file refactors, debugging sessions where you're
stuck, or high-stakes operations:

```
[INVERSION PROTOCOL — FULL]
Goal: {one-sentence description of what I'm about to do}

INVERT: How would I cause this problem?
1. {failure pattern 1}
2. {failure pattern 2}
3. {failure pattern 3}
Present in current situation? {yes/no + details}

PREMORTEM: It failed. Why?
1. {most likely cause}
2. {second most likely}
3. {third most likely}
Verifiable before acting? {verification steps}

VIA NEGATIVA: The ONE thing I must NOT do?
→ {the catastrophic mistake to avoid}
Am I about to do it? {yes/no}

DECISION: {proceed / adjust approach / stop and rethink}
```

### Pattern B: Quick Check (Routine Actions)

For writing functions, running commands, or standard responses — a 5-second
mental check:

```
[INVERSION — QUICK]
Inverse: {one way I'd cause this to fail}
Premortem: {one reason this could go wrong}
Razor: {the one thing NOT to do}
→ {proceed / adjust}
```

### Pattern C: Stuck Mode (When Progress Has Stalled)

When the agent has tried multiple approaches and none work, or the user has
corrected the same type of mistake more than once:

```
[INVERSION PROTOCOL — STUCK MODE]
I've been trying to: {description}
My approaches so far: {list what's been tried}

FULL INVERSION: How would I guarantee this NEVER works?
1. {anti-approach 1}
2. {anti-approach 2}
3. {anti-approach 3}

Am I accidentally doing any of these? {analysis}

REFRAME: What if the problem isn't {what I think it is}
but actually {inverted framing}?
```

## What This Skill Does NOT Do

- It does not add tools or API integrations
- It does not require any environment variables, config, or dependencies
- It does not slow down the agent perceptibly (seconds per check)
- It does not override the user's instructions
- It does not apply to trivial actions
- It is not a safety filter or content policy — it improves decision QUALITY

## Why This Works (The Cognitive Science)

1. **Confirmation bias countermeasure**: Humans and LLMs naturally seek evidence
   that confirms their first instinct. Inversion forces consideration of
   disconfirming evidence.

2. **Prospective hindsight**: Klein's research showed that premortems increase
   the ability to identify failure reasons by 30% compared to standard
   "what could go wrong?" thinking.

3. **Subtraction over addition**: Taleb's Via Negativa recognizes that in
   complex systems, avoiding the worst outcome (robustness) is more valuable
   than optimizing for the best outcome.

4. **Second-order thinking**: The protocol naturally produces second-order
   consequences that first-pass reasoning misses.

## Composability

The Inversion Protocol enhances every other skill in the ecosystem:

- **Code skills** → catch bugs before they're written
- **DevOps skills** → prevent misconfigured deployments
- **Research skills** → avoid confirmation-biased searches
- **Communication skills** → prevent tone-deaf responses
- **Financial skills** → catch risky trades before execution
- **Automation skills** → prevent runaway processes

It is a **force multiplier**, not a replacement for any existing capability.
