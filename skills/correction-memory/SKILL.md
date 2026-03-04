---
name: correction-memory
version: 1.1.0
description: Makes agent corrections persistent and reusable. When you override, reject, or correct an agent's output, this skill logs the correction and automatically injects it into future spawns of the same agent type. Solves "agent keeps making the same mistake across sessions." Installs correction-tracker lib + injection hook into agent-context-loader. Works standalone or alongside intent-engineering skill.
---

# Correction Memory

## The Problem

When you correct an agent, that correction evaporates after the session. Next time you spawn the same agent type, it makes the same mistake. There's no memory of what you've already taught it.

## What This Skill Installs

- **`lib/correction-tracker.js`** — logs corrections per agent type to `memory/corrections/[AgentType].jsonl`
- **Hook into `agent-context-loader.js`** — correction preamble prepended to spawns automatically (if intent-engineering is also installed)

## Installation

### Step 1 — Install correction-tracker

```bash
cp references/correction-tracker-template.js $OPENCLAW_WORKSPACE/lib/correction-tracker.js
```

Verify it runs:

```bash
node $OPENCLAW_WORKSPACE/lib/correction-tracker.js
```

### Step 2 — Wire agent-context-loader (if using intent-engineering)

If `lib/agent-context-loader.js` is installed (from intent-engineering skill), correction injection is **automatic** — no wiring needed. The loader checks for `correction-tracker.js` at startup and loads it if present.

If you are NOT using intent-engineering, add this to your spawn logic manually:

```javascript
const { buildCorrectionPreamble } = require('./lib/correction-tracker');

const agentType   = 'CoderAgent'; // or whatever agent you're spawning
const corrections = buildCorrectionPreamble(agentType, workspaceRoot);
const fullTask    = corrections ? corrections + '\n\n---\n\n' + originalTask : originalTask;
```

## Logging Corrections

### Programmatic

```javascript
const { logCorrection } = require('./lib/correction-tracker');

logCorrection(
  'CoderAgent',                                    // agent type
  'Used ESM import instead of require()',          // what was wrong
  'Always use require() for Node.js stdlib modules', // correct behavior
  workspaceRoot,
  { session_channel: 'discord' }                  // optional metadata
);
```

### Via main agent (natural language)

Just tell the main agent:

> "Note that [AgentType]: [what it did wrong] — [correct behavior]"

The main agent will log it programmatically.

## How Corrections Are Replayed

On every subagent spawn, `agent-context-loader` detects the agent type from the task description and prepends:

```
## Corrections from Previous Sessions

The following corrections were logged for CoderAgent. Apply these behaviors:

1. **[2026-03-01] Issue:** Used ESM import instead of require()
   **Correction:** Always use require() for Node.js stdlib modules
```

Only corrections from the **last 30 days** are injected. Older corrections expire automatically — stale rules don't accumulate.

## Viewing Corrections

```bash
# All corrections for an agent type
cat $OPENCLAW_WORKSPACE/memory/corrections/CoderAgent.jsonl | jq .

# List all agent types with corrections
ls $OPENCLAW_WORKSPACE/memory/corrections/

# Count corrections per agent
for f in $OPENCLAW_WORKSPACE/memory/corrections/*.jsonl; do
  echo "$(basename $f .jsonl): $(wc -l < $f) corrections"
done
```

## Agent Type Detection

The loader auto-detects agent type from the task description. Default rules:

| Task keywords | Agent type |
|---|---|
| `code`, `coder`, `impl`, `debug` | `CoderAgent` |
| `writ`, `author`, `novel`, `chapter` | `AuthorAgent` |
| `world`, `build` | `WorldbuilderAgent` |
| (anything else) | `general` |

To add custom agent types, edit `detectAgentType()` in `agent-context-loader.js`.

## References

- `references/correction-tracker-template.js` — Full implementation of correction-tracker.js
