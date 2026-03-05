---
name: intent-engineering
description: Adds a machine-readable intent layer to OpenClaw agents. Creates INTENT.md (optimization priorities, tradeoffs, delegation rules), wires it into subagent spawns via agent-context-loader, and ensures every subagent knows what you're optimizing for — not just what to do. Solves the "Klarna failure mode": AI optimizes measurable metrics instead of actual goals. Use when setting up a new OpenClaw workspace, when subagents keep making the wrong tradeoffs, or when you want explicit control over cost/quality/speed priorities.
---

# Intent Engineering

## The Problem

Without an intent layer, agents optimize for what's measurable (fast response, no errors) rather than what matters (your actual priorities). The Klarna failure: AI saved $60M and destroyed customer loyalty because it optimized resolution time, not relationships.

## What This Skill Installs

1. **`INTENT.md`** — YAML priority manifest at workspace root
2. **`lib/agent-context-loader.js`** — prepends intent summary to every subagent spawn
3. **Routing integration** — intent propagation flag in all routing decisions

## Installation

### Step 1 — Create INTENT.md

Copy `references/intent-template.md` to your workspace root as `INTENT.md` and edit:

```bash
cp $(dirname $0)/references/intent-template.md $OPENCLAW_WORKSPACE/INTENT.md
```

Or create it manually — see `references/intent-template.md` for the annotated schema.

### Step 2 — Install agent-context-loader

Copy the reference implementation to `lib/`:

```bash
cp $(dirname $0)/references/agent-context-loader-template.js $OPENCLAW_WORKSPACE/lib/agent-context-loader.js
```

Verify it runs:

```bash
node $OPENCLAW_WORKSPACE/lib/agent-context-loader.js $OPENCLAW_WORKSPACE
```

### Step 3 — Wire into spawn calls

In any subagent spawn, prepend the intent context to the task description:

```javascript
const { prepareAgentContext } = require('./lib/agent-context-loader');

const { context } = prepareAgentContext(taskType, workspaceRoot);
const fullTask = context ? context + '\n\n---\n\n' + originalTask : originalTask;

// Use fullTask as your subagent task description
```

`taskType` is a string describing the work (e.g. `"code_review"`, `"research"`, `"writing"`). The loader extracts relevant context from INTENT.md and recent memory automatically.

### Step 4 — Verify

Spawn a test subagent with a task that would normally trigger a tradeoff (cost vs quality, speed vs depth). Confirm the subagent's output reflects your priorities from INTENT.md.

## INTENT.md Structure

| Field | Purpose |
|---|---|
| `optimization_priority` | Ordered priorities: primary → never_sacrifice |
| `tradeoffs` | Explicit rules when objectives conflict |
| `model_tier_intent` | Which task types get which model tier |
| `delegation_intent` | When to delegate vs handle inline |
| `quality_intent` | Per-domain quality standards |

See `references/intent-template.md` for the full annotated template.

## How It Works

`prepareAgentContext()` reads INTENT.md fresh on every call, extracts a compact summary (≤200 chars), and prepends it to the spawn task. Subagents receive:

```
## Intent
Optimize for: user_value > honesty > cost. Never sacrifice: honesty, safety.
Delegate when blocking chat. Prefer depth for architecture/writing.
```

If INTENT.md is missing, a safe default is injected. The loader never throws — it degrades silently.

## References

- `references/intent-template.md` — Full annotated INTENT.md template with all fields
- `references/agent-context-loader-template.js` — Complete agent-context-loader.js implementation
