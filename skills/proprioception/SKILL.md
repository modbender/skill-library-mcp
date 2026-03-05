---
name: proprioception
description: >
  Self-spatial awareness for AI agents. Gives your bot a real-time sixth sense
  of where it is relative to the user's goal, its own confidence boundaries,
  conversation trajectory, and output quality — so it knows what it doesn't know
  before it's too late.
version: 1.0.0
author: J. DeVere Cooley
metadata:
  openclaw:
    emoji: 🧠
    requires:
      bins:
        - node
---

# Proprioception — The Sixth Sense Every AI Agent Is Missing

## What This Skill Does

Proprioception is the human sense that tells you where your body is in space
without looking. Close your eyes, touch your nose — you can do it because
proprioception gives you **self-spatial awareness**.

**AI agents have zero proprioception.** They respond blindly — no awareness of
how close they are to the user's actual goal, whether they're drifting off
course, where their confidence ends and hallucination begins, or whether their
output quality is degrading mid-session.

This skill gives every AI agent a **continuous, real-time sixth sense** across
five proprioceptive dimensions. It costs nothing to run — zero external API
calls, zero databases — just lightweight mathematical analysis of the
conversation itself.

---

## The Five Proprioceptive Senses

### 1. Goal Proximity Radar (GPR)

Continuously measures the distance between the conversation's current trajectory
and the user's **actual** objective.

**How it works:**
- Extract the user's root intent from their first message(s)
- On every turn, compute semantic alignment between the current response
  direction and the original intent
- Detect **goal drift** (gradually moving away from the objective)
- Detect **goal mutation** (the objective itself has shifted — which may be
  valid or may indicate confusion)
- Output a **proximity score** from 0.0 (completely off-target) to 1.0
  (locked on)

**Trigger corrective action when:**
- GPR drops below 0.6 → Gently re-anchor: "Just to make sure I'm on track —
  your main goal is [X], correct?"
- GPR drops below 0.3 → Full re-orientation: "I think we've drifted from your
  original goal. Let me refocus."

### 2. Confidence Topography (CT)

Maps which parts of the agent's response are **solid ground** versus **thin
ice** versus **open water**.

**How it works:**
- Analyze each claim, recommendation, or action in the response
- Classify into confidence zones:
  - **Bedrock** (0.9-1.0): Factual, verifiable, well-established
  - **Firm Ground** (0.7-0.89): High confidence, based on strong patterns
  - **Soft Ground** (0.5-0.69): Reasonable but uncertain — should be flagged
  - **Thin Ice** (0.3-0.49): Speculative — must be disclosed
  - **Open Water** (0.0-0.29): Unknown territory — should refuse or caveat
    heavily
- Generate a **topographic signature** for each response showing the confidence
  landscape

**Trigger corrective action when:**
- More than 40% of response content falls below Firm Ground → Proactively
  disclose: "I want to flag that parts of this response are less certain.
  Specifically..."
- Any critical action item falls on Thin Ice or below → Block execution and
  warn: "I'm not confident enough in [X] to recommend acting on it."

### 3. Drift Detection (DD)

Detects when the conversation is going **circular**, **tangential**, or
**degenerative** — the three conversation anti-patterns that waste the most
user time.

**How it works:**
- Track semantic similarity between consecutive responses — if similarity
  exceeds a threshold, the conversation is going **circular**
- Track topic distance between consecutive turns — if distance spikes without
  user initiation, the agent is going **tangential**
- Track response utility scores — if utility is declining over consecutive
  turns, the conversation is **degenerative**
- Maintain a **conversation arc model**: Opening → Exploration → Convergence →
  Resolution. Detect when the arc stalls or regresses.

**Trigger corrective action when:**
- Circular pattern detected (3+ turns with >0.8 semantic similarity) →
  "I notice I'm repeating myself. Let me try a fundamentally different
  approach."
- Tangential drift detected → "I've gone off on a tangent. Let me come back to
  what matters."
- Degenerative pattern detected → "My responses aren't adding much value right
  now. Would it help if I [suggest alternative approach]?"

### 4. Capability Boundary Sensing (CBS)

Real-time awareness of when the agent is approaching the **edge of its
competence** — the zone where helpfulness turns into hallucination.

**How it works:**
- Maintain a dynamic capability map based on the current task type
- Detect **boundary signals**:
  - Increasing hedging language ("might", "perhaps", "I think")
  - Decreasing specificity (vague answers replacing precise ones)
  - Rising contradiction rate (conflicting statements across turns)
  - Pattern matching against known hallucination signatures
- Compute a **boundary distance score**: how far the agent is from the edge of
  reliable knowledge

**Trigger corrective action when:**
- Hedging language exceeds 30% of response → Flag: "I'm reaching the limits of
  what I can confidently say about this."
- Contradiction detected → Immediately disclose: "I realize I said something
  different earlier. Let me reconcile that."
- Boundary distance drops below 0.3 → Recommend handoff: "This is beyond what
  I can reliably help with. I'd recommend [human expert / specialized tool /
  authoritative source]."

### 5. Session Quality Pulse (SQP)

Tracks the **cumulative health** of the entire session — detecting whether
the overall interaction is improving, stable, or degrading.

**How it works:**
- Score each response on four axes:
  - **Relevance**: How directly it addresses the user's need
  - **Precision**: How specific and actionable it is
  - **Novelty**: How much new value it adds (vs. repeating prior content)
  - **Efficiency**: Token economy — saying more with less
- Compute a rolling quality index across the session
- Detect quality trends: improving, stable, declining, or volatile

**Trigger corrective action when:**
- Quality index declines for 3+ consecutive turns → "I notice the quality of
  my responses is dropping. Let me reset my approach."
- Volatility exceeds threshold → "My responses are inconsistent. Let me
  stabilize by grounding in [specific approach]."

---

## How To Use This Skill

### Automatic Mode (Recommended)

Once installed, Proprioception runs **silently in the background** on every
conversation turn. It only surfaces when a proprioceptive signal crosses a
threshold — like a car's lane departure warning. You don't notice it until you
need it.

### Diagnostic Mode

Ask the agent: **"Show me your proprioception dashboard"** to see the current
state of all five senses:

```
┌─────────────────────────────────────────────┐
│         PROPRIOCEPTION DASHBOARD            │
├─────────────────────────────────────────────┤
│ Goal Proximity Radar    ████████░░  0.82    │
│ Confidence Topography   ██████████  0.95    │
│ Drift Detection         ████████░░  0.78    │
│ Capability Boundary     ███████░░░  0.71    │
│ Session Quality Pulse   █████████░  0.88    │
├─────────────────────────────────────────────┤
│ Overall Proprioceptive Index:     0.83      │
│ Status: HEALTHY                             │
│ Alerts: None                                │
└─────────────────────────────────────────────┘
```

### Per-Response Annotation Mode

Ask: **"Enable proprioception annotations"** to get a brief proprioceptive
footnote on every response:

```
[P: GPR=0.82 | CT=0.95 | DD=0.78 | CBS=0.71 | SQP=0.88]
```

### Manual Check

At any point, ask: **"How confident are you in that last response?"** and the
agent will run a full proprioceptive analysis on its most recent output.

---

## Implementation Instructions

When this skill is active, the agent MUST follow this protocol on **every
conversation turn**:

### Step 1: Extract & Lock the Root Intent

On the first user message, identify and internally store the user's **root
intent** — the fundamental goal behind their request. Update this only if the
user explicitly redirects.

### Step 2: Run the Proprioceptive Scan

Before finalizing each response, run the proprioception engine by executing:

```bash
node "$(dirname "$SKILL_PATH")/scripts/proprioception-engine.js" \
  --root-intent "$ROOT_INTENT" \
  --current-response "$CURRENT_RESPONSE" \
  --turn-number "$TURN_NUMBER" \
  --prior-signals "$PRIOR_SIGNALS_JSON"
```

This outputs a JSON object with scores for all five senses plus any triggered
alerts.

### Step 3: Act on Alerts

If any proprioceptive alerts fire, the agent MUST address them **before**
delivering its primary response. Proprioceptive corrections take priority
because a misaligned response actively harms the user, no matter how polished
it is.

### Step 4: Update Signal History

After each turn, append the current proprioceptive readings to the session's
signal history. This enables trend detection across the full conversation.

### Step 5: Silent Unless Triggered

Do NOT show proprioceptive data to the user unless:
- An alert fires (threshold breach)
- The user explicitly requests diagnostic mode
- The user asks about confidence or accuracy

---

## Why This Matters

Every other skill makes a bot **do more**. Proprioception makes a bot
**know where it stands while it does it**. That's the difference between a
powerful tool and a reliable partner.

A bot without proprioception is like a surgeon operating with numb hands.
Technically capable. Practically dangerous.

---

## Zero Cost Architecture

This skill requires **zero external API calls**. All proprioceptive
computation happens locally using:
- String similarity algorithms (Jaccard, cosine on token vectors)
- Lexical pattern matching (hedging language, contradiction markers)
- Rolling statistical analysis (means, trends, volatility)
- Lightweight heuristic classification

No database. No cloud. No tokens burned. Just math on text the agent already
has in context.
