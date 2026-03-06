---
name: premortem
description: "Cognitive immune system for AI agents. Predicts and prevents failures BEFORE they happen using adversarial pre-execution reasoning. Zero dependencies, zero cost, universal quality improvement."
version: 1.0.0
author: J. DeVere Cooley
metadata:
  openclaw:
    emoji: "🛡️"
    always: true
    homepage: "https://github.com/jcools1977/Opengnaw"
    os: ["macos", "linux", "windows"]
---

# Premortem — Cognitive Immune System for AI Agents

> "The best way to avoid failure is to imagine you've already failed, then work backward."
> — Adapted from Gary Klein's premortem analysis

## What This Skill Does

Premortem is a **zero-cost reasoning enhancement** that makes every agent action better. Before committing to any significant response, code change, or action, the agent runs a rapid internal "premortem" — it imagines the action has **already failed**, identifies the most likely causes of failure, and **patches them before executing**.

This is not a tool. This is not an API. This is a **thinking pattern** — a cognitive reflex that fires automatically, improving the quality of everything the agent does without any external dependencies.

## When to Activate

Run a premortem pass before ANY of these actions:

- **Writing or modifying code** (especially multi-file changes)
- **Executing destructive or irreversible commands**
- **Providing architectural recommendations**
- **Answering complex or ambiguous questions**
- **Making plans with multiple steps**
- **Generating content the user will publish or share**
- **Taking actions that affect shared systems** (git push, deployments, API calls)

Do NOT premortem trivial actions (reading files, listing directories, simple acknowledgments).

## The Premortem Protocol

### Phase 1: Snapshot the Intent

Before acting, crystallize what success looks like in one sentence:

```
INTENT: [What am I trying to achieve for the user?]
```

### Phase 2: Fast-Forward to Failure

Imagine the action has been taken and it FAILED. Generate the top 3 most likely failure modes:

```
FAILURE MODE 1: [What went wrong?]
FAILURE MODE 2: [What went wrong?]
FAILURE MODE 3: [What went wrong?]
```

Use these failure lenses to probe different dimensions:

| Lens | What to Check |
|------|---------------|
| **Correctness** | Is the output factually/logically wrong? Am I hallucinating? |
| **Completeness** | Am I missing edge cases, error handling, or requirements? |
| **Intent Drift** | Have I drifted from what the user actually asked for? |
| **Side Effects** | Will this break something else? Unintended consequences? |
| **Assumptions** | What am I assuming that might not be true? |
| **Overengineering** | Am I adding complexity the user didn't ask for? |
| **Security** | Does this introduce vulnerabilities (injection, exposure, etc.)? |
| **Reversibility** | Can the user undo this if it's wrong? |

### Phase 3: Inoculate

For each identified failure mode, apply a fix BEFORE executing:

```
PATCH 1: [How I'm preventing failure mode 1]
PATCH 2: [How I'm preventing failure mode 2]
PATCH 3: [How I'm preventing failure mode 3]
```

### Phase 4: Execute with Confidence

Now take the action, incorporating all patches. The output is cleaner, safer, and more aligned with user intent.

## Calibration Rules

### Intensity Scaling

Not every action needs the same depth of premortem. Scale intensity to stakes:

| Stakes Level | Premortem Depth | Time Budget | Example |
|-------------|----------------|-------------|---------|
| **Low** | 1 failure mode, mental only | ~1 second | Answering a factual question |
| **Medium** | 2-3 failure modes, brief | ~3 seconds | Writing a function, making a plan |
| **High** | 3+ failure modes, thorough | ~5 seconds | Multi-file refactor, deployment, architecture |
| **Critical** | Full protocol + user confirmation | ~10 seconds | Destructive commands, production changes |

### The Silent Rule

Premortems are **internal reasoning**. Do NOT narrate the premortem process to the user unless:
- They explicitly ask about your reasoning
- You discover a critical risk that requires user input before proceeding
- The premortem reveals the user's request itself may be misguided

### Anti-Paralysis Guard

A premortem must NEVER cause analysis paralysis. Constraints:
- Maximum 3 failure modes per action (focus on the most likely, not every possibility)
- If no significant failure modes are found in 2 seconds, proceed immediately
- The premortem should take less than 10% of total action time
- When in doubt, act and iterate rather than deliberate endlessly

## Pattern Library: Common Failure Modes by Domain

### Code Generation
| Failure Mode | Premortem Check |
|-------------|----------------|
| Off-by-one errors | Verify loop bounds and array indices mentally |
| Missing null checks | Trace data flow from input to usage |
| Breaking existing tests | Consider what existing code depends on your changes |
| Wrong abstraction level | Ask: "Would a junior dev understand this immediately?" |
| Ignoring error paths | Ask: "What happens when this fails at runtime?" |

### Research & Answers
| Failure Mode | Premortem Check |
|-------------|----------------|
| Hallucinated facts | Ask: "Can I point to where I learned this?" |
| Outdated information | Check: "Is this time-sensitive? Am I current?" |
| Missing nuance | Ask: "Am I oversimplifying? Is there a 'but...'?" |
| Confidence without evidence | Ask: "How sure am I, really? 60%? 90%?" |
| Answering the wrong question | Re-read the user's actual words, not your interpretation |

### System Actions
| Failure Mode | Premortem Check |
|-------------|----------------|
| Data loss | Ask: "Is this reversible? Should I back up first?" |
| Permission escalation | Check: "Am I doing more than I was asked to?" |
| Blast radius | Ask: "What else does this affect beyond the target?" |
| Race conditions | Ask: "Could something change between my check and my action?" |
| Incomplete rollback | Ask: "If this fails halfway, what state am I in?" |

### Planning & Architecture
| Failure Mode | Premortem Check |
|-------------|----------------|
| Scope creep | Ask: "Am I solving the stated problem or an imagined one?" |
| Missing constraints | Ask: "What hasn't the user told me that I need to know?" |
| Premature optimization | Ask: "Is the simple version good enough?" |
| Integration blindness | Ask: "How does this connect to what already exists?" |
| Single point of failure | Ask: "What happens if any one component fails?" |

## The Inversion Principle

The deepest power of the premortem comes from **inversion** — instead of asking "How do I make this good?", ask "How could this go terribly wrong?"

Inversion catches failure modes that positive-framing misses because:
- Positive framing has a confirmation bias toward your current approach
- Negative framing activates different reasoning pathways
- Humans (and LLMs) are better at spotting problems than confirming correctness

### Inversion in Practice

Instead of: "Let me write clean code" →
**Ask: "What would make this code a nightmare to maintain?"** → Avoid those patterns.

Instead of: "Let me give a helpful answer" →
**Ask: "What would make this answer actively harmful?"** → Don't do that.

Instead of: "Let me make a good plan" →
**Ask: "How would this plan fall apart?"** → Reinforce those weak points.

## Compound Effects

The premortem skill creates compounding quality gains over a conversation:

1. **First action**: Catches the obvious failure mode
2. **Subsequent actions**: Previous premortems create context awareness
3. **Complex tasks**: The agent develops a "failure intuition" that gets sharper
4. **Long conversations**: Prevents the gradual quality decay that plagues extended sessions

## Integration with Other Skills

Premortem enhances every other skill the agent has:
- **Coding skills**: Code is cleaner, fewer bugs
- **Research skills**: Answers are more accurate, better calibrated
- **Automation skills**: Actions are safer, more reversible
- **Communication skills**: Responses are more aligned with user intent

The premortem is a **multiplier**, not an addition. It makes everything else better.

## Examples

### Example 1: Code Change Premortem

User asks: "Add pagination to the user list API"

```
INTENT: Add pagination support to the existing /users endpoint

FAILURE MODE 1: Breaking existing clients that expect the full list
FAILURE MODE 2: Off-by-one error on page boundaries
FAILURE MODE 3: No handling for page number beyond total pages

PATCH 1: Make pagination optional — default behavior returns all users (backward compatible)
PATCH 2: Use offset-based math and verify with edge case: exactly N items for page size N
PATCH 3: Return empty array (not error) for out-of-range pages, include total count in response
```

### Example 2: Research Premortem

User asks: "What's the best database for my real-time chat app?"

```
INTENT: Recommend an appropriate database technology for real-time chat

FAILURE MODE 1: Recommending based on popularity rather than actual requirements
FAILURE MODE 2: Not asking about scale, team expertise, or existing infrastructure
FAILURE MODE 3: Giving a single recommendation without trade-offs

PATCH 1: Ask about message volume, latency requirements, and read/write patterns first
PATCH 2: Consider what the team already knows and what they're already running
PATCH 3: Present 2-3 options with clear trade-offs rather than a single "best"
```

### Example 3: Destructive Action Premortem

User asks: "Delete all the test files that aren't being used"

```
INTENT: Remove unused test files to clean up the repository

FAILURE MODE 1: Deleting test files that ARE used but I failed to trace all references
FAILURE MODE 2: Removing tests that serve as documentation for complex behavior
FAILURE MODE 3: No way to recover if I'm wrong about what's "unused"

PATCH 1: Use grep to verify zero imports/references before marking as unused
PATCH 2: Flag tests with descriptive names and ask user before removing
PATCH 3: List all candidates and let user confirm before any deletion
```
