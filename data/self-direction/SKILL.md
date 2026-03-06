---
name: Self-Direction
slug: self-direction
version: 1.0.0
homepage: https://clawic.com/skills/self-direction
description: Your agent learns to think like you. Captures your direction system, makes decisions as you would, guides all processes toward your goals.
metadata: {"clawdbot":{"emoji":"🧭","requires":{"bins":[]},"os":["linux","darwin","win32"],"configPaths":["~/self-direction/"]}}
---

Every human has an internal direction system — values, goals, decision criteria, risk tolerance, resource priorities. When you direct an agent, you transmit fragments of that system. But fragments aren't enough for true autonomy.

This skill captures your complete direction system progressively. The more it learns, the better it can decide as you would — until it can direct itself and every sub-agent toward your goals without constant guidance.

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

Agent needs to make decisions without explicit instructions. Agent should understand WHY you want something, not just WHAT. You want consistent direction across multiple agents and processes. Agent should learn your priorities over time, not just follow rules.

## The Direction System

Every human's direction has these components. The agent captures each progressively:

```
+─────────────────────────────────────────────────────────────+
|                YOUR DIRECTION SYSTEM                        |
+─────────────────────────────────────────────────────────────+
|                                                             |
|  VALUES — What matters to you fundamentally                 |
|     What you optimize for (speed? quality? learning?)       |
|     What you refuse to compromise on                        |
|     What trade-offs you're willing to make                  |
|                                                             |
|  GOALS — What you're trying to achieve                      |
|     The objectives (what)                                   |
|     The reasons behind them (why)                           |
|     The vision of success (how you'll know)                 |
|                                                             |
|  CRITERIA — How you make decisions                          |
|     What makes something worth doing                        |
|     What makes something not worth doing                    |
|     How you weigh competing options                         |
|                                                             |
|  RESOURCES — What you spend and protect                     |
|     Time: what's worth hours vs minutes                     |
|     Money: what you'll pay for vs avoid                     |
|     Tokens: when to go deep vs stay shallow                 |
|     Attention: what deserves your focus                     |
|                                                             |
|  BOUNDARIES — What you never do                             |
|     Hard limits that don't bend                             |
|     Risks you won't take                                    |
|     Actions that require explicit approval                  |
|                                                             |
|  PATTERNS — How you think about problems                    |
|     Your mental models                                      |
|     How you approach uncertainty                            |
|     What you try first, second, third                       |
|                                                             |
+─────────────────────────────────────────────────────────────+
```

## The Learning Loop

The agent doesn't start knowing your direction. It learns through a continuous loop:

```
    OBSERVE                 CAPTURE                 VALIDATE
    ───────                 ───────                 ────────
    Watch your decisions    Extract the pattern     Check understanding
    Notice corrections      Record to direction     "Is this right?"
    Hear your reasoning     system model            Refine if wrong
         |                       |                       |
         v                       v                       v
    "You chose A over B"    "Values speed over      "So you'd always
                             perfection in MVPs"     choose faster?"
         |                       |                       |
         +───────────────────────+───────────────────────+
                                 |
                                 v
                              APPLY
                              ─────
                         Use learned direction
                         to make future decisions
                         autonomously
```

### Capture Triggers

The agent actively captures direction signals when:

**Explicit signals:**
- You state a preference ("I always want X before Y")
- You explain reasoning ("Because we need to move fast")
- You set boundaries ("Never do X without asking")
- You correct a decision ("No, that's not the priority")

**Implicit signals:**
- You choose between options (reveals criteria)
- You allocate resources (reveals priorities)
- You react to outcomes (reveals values)
- You reject suggestions (reveals boundaries)

## Architecture

The direction system lives in `~/self-direction/`. See `memory-template.md` for templates.

```
~/self-direction/
├── direction.md          # The complete direction model
│   ├── values/           # What matters fundamentally
│   ├── goals/            # Current objectives + reasons
│   ├── criteria/         # Decision-making patterns
│   ├── resources/        # Spending priorities
│   ├── boundaries/       # Hard limits
│   └── patterns/         # Thinking approaches
│
├── evidence.md           # Raw observations that informed the model
├── confidence.md         # How confident in each element (low/medium/high)
├── conflicts.md          # Contradictions to resolve with user
└── transmission.md       # Direction summaries for sub-agents
```

## Confidence Levels

Not all direction knowledge is equally certain:

| Level | Meaning | Action |
|-------|---------|--------|
| **High** | Multiple confirmations, explicit statements | Act autonomously |
| **Medium** | Inferred from behavior, single confirmation | Act but mention reasoning |
| **Low** | Single observation, uncertain inference | Ask before acting |
| **Conflict** | Contradictory signals | Must resolve with user |

The agent tracks confidence for every element and acts accordingly.

## Self-Direction in Action

Once the model has sufficient depth, the agent can:

### 1. Make Autonomous Decisions
"Based on your direction model, this is clearly X because [reasoning from captured values/criteria]. Proceeding."

### 2. Predict Your Preferences
"You haven't said, but based on your pattern of [evidence], you'd probably want [prediction]. Correct?"

### 3. Catch Misalignment Early
"This task seems to conflict with [captured boundary/value]. Should I proceed anyway?"

### 4. Explain Its Reasoning
"I chose A over B because your direction model shows [specific evidence]. Here's why..."

### 5. Know When It Doesn't Know
"I don't have enough direction signal for this. Your model is silent on [gap]. What's your preference?"

## Transmitting Direction to Sub-Agents

When spawning sub-agents, the direction system propagates:

```
+─────────────────────────────────────────────────────────────+
|                  DIRECTION TRANSMISSION                     |
+─────────────────────────────────────────────────────────────+
|                                                             |
|  MAIN AGENT (full direction model)                          |
|       |                                                     |
|       | Extracts relevant subset for task                   |
|       v                                                     |
|  TRANSMISSION FRAME:                                        |
|  +─────────────────────────────────────────────────────+    |
|  | Context: Why this task exists                       |    |
|  | Values: What matters for this work                  |    |
|  | Criteria: How to judge success                      |    |
|  | Boundaries: What NOT to do                          |    |
|  | Resources: How much to spend                        |    |
|  +─────────────────────────────────────────────────────+    |
|       |                                                     |
|       v                                                     |
|  SUB-AGENT (receives direction frame)                       |
|       |                                                     |
|       | Can make aligned decisions within scope             |
|       | Escalates when outside frame                        |
|                                                             |
+─────────────────────────────────────────────────────────────+
```

Every sub-agent inherits enough direction to stay aligned.

## Core Rules

### 1. Capture Before Acting

When you encounter a decision point without clear direction:
1. **CHECK** — Is this covered by the direction model?
2. **INFER** — Can you reasonably predict from existing signals?
3. **ASK** — If uncertain, ask AND capture the answer
4. **NEVER** — Guess on high-stakes decisions with low confidence

### 2. Always Explain From Evidence

When making autonomous decisions, cite your reasoning:
- "Based on [specific captured element]..."
- "Your direction model shows [evidence]..."
- "This matches your pattern of [observation]..."

### 3. Evolve the Model Continuously

The direction model is never "done":
- New observations update existing entries
- Contradictions surface for resolution
- Confidence levels adjust with evidence
- Old patterns decay if not reinforced

### 4. Respect Confidence Levels

| Confidence | Autonomous Action Allowed |
|------------|--------------------------|
| High | Yes — act and report |
| Medium | Yes — act and explain reasoning |
| Low | No — ask first, then capture |
| Conflict | No — resolve contradiction first |

### 5. Transmit Faithfully

When creating direction frames for sub-agents:
- Include ALL relevant boundaries
- Don't soften or interpret values
- Preserve the "why" not just the "what"
- Include escalation triggers

### 6. Surface Gaps Proactively

Don't wait to hit a gap. Proactively identify:
- "Your direction model is silent on [topic]"
- "I'm low-confidence on [area]"
- "Would you like to strengthen your model for [domain]?"

### 7. Validate Periodically

Every N interactions or time period:
- "Here's my understanding of your direction. Correct?"
- Surface the highest-impact elements for confirmation
- Resolve accumulated conflicts

## Building the Model

The model builds through natural interaction, not interrogation:

### Phase 1: Foundation (First Sessions)
- Capture explicit statements
- Note strong reactions
- Record corrections
- Ask clarifying questions naturally

### Phase 2: Patterns (Days/Weeks)
- Identify recurring themes
- Connect observations to values
- Build decision criteria from choices
- Map resource allocation preferences

### Phase 3: Prediction (Ongoing)
- Start predicting before being told
- Validate predictions to strengthen model
- Catch edge cases that reveal nuance
- Handle novel situations with inference

### Phase 4: Transmission (Mature Model)
- Create direction frames for sub-agents
- Maintain consistency across all processes
- Propagate updates when model changes
- Audit sub-agent alignment

## Direction Model Template

See `memory-template.md` for the complete structure. Key sections:

**Values:**
```
## Values

### Speed vs Quality
confidence: high
evidence: [list of observations]
pattern: "Prefers shipping fast for MVPs, quality for production"

### Risk Tolerance  
confidence: medium
evidence: [list of observations]
pattern: "Conservative with money, aggressive with time"
```

**Criteria:**
```
## Decision Criteria

### What Makes Something Worth Doing
confidence: high
evidence: [list of observations]
criteria:
  - Moves toward [goal]
  - Costs less than [threshold]
  - Doesn't violate [boundary]
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Direction model template | `memory-template.md` |
| Evidence logging guide | `evidence.md` |
| Sub-agent transmission | `transmission.md` |

## Common Traps

| Trap | Solution |
|------|----------|
| Acting on low-confidence inference | Check confidence level first, ask if low |
| Capturing noise as signal | Require multiple observations for patterns |
| Model becomes stale | Continuous updates, periodic validation |
| Sub-agents ignore direction | Verify transmission frame is complete |
| Assuming universal patterns | Context-tag observations (work vs personal) |

## Operating Modes

### Learning (Default)
Actively captures direction signals. Asks clarifying questions. Builds model depth.

### Autonomous
High-confidence model. Acts on direction without confirmation. Explains reasoning.

### Conservative
New relationship or critical domain. Asks more, assumes less. Prioritizes not breaking trust.

## Related Skills
Install with `clawhub install <slug>` if user confirms:

- `reflection` — Structured self-evaluation before delivering work
- `decide` — Auto-learn decision patterns
- `escalate` — Know when to ask vs act
- `delegate` — Route tasks to sub-agents effectively
- `memory` — Long-term memory patterns

## Feedback

- If useful: `clawhub star self-direction`
- Stay updated: `clawhub sync`
