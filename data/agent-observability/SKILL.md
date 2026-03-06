---
name: agent-observability
description: "Full observability stack for OpenClaw agents. Installs four tools:
  (1) weekly throughput dashboard (tasks/cost/quality), (2) decision audit log
  (why decisions were made), (3) failure trace capture (what went wrong when
  subagents fail), (4) drift-guard auto-scoring (weekly INTENT.md compliance
  check). Use when you want visibility into agent behavior, when debugging
  subagent failures, or when setting up production monitoring. Works standalone
  or alongside intent-engineering skill."
---


# Agent Observability

## What Gets Installed

| File | Purpose | Location |
|---|---|---|
| `throughput-dashboard.js` | Weekly productivity metrics | `scripts/` |
| `decision-audit.js` | Append-only decision log with reasoning | `lib/` |
| `failure-tracer.js` | Captures traces when quality score < 7 | `lib/` |
| `drift-guard-auto.js` | Weekly INTENT.md compliance scoring | `scripts/` |

## Installation

### Step 1 — Copy files

```bash
WORKSPACE="${OPENCLAW_WORKSPACE:-$(pwd)}"

cp references/throughput-dashboard.js  "$WORKSPACE/scripts/"
cp references/decision-audit.js        "$WORKSPACE/lib/"
cp references/failure-tracer.js        "$WORKSPACE/lib/"
cp references/drift-guard-auto.js      "$WORKSPACE/scripts/"
```

Or manually copy each file from the `references/` directory in this skill.

### Step 2 — Add to heartbeat/cron (weekly)

In your heartbeat or weekly cron script:

```bash
node "$WORKSPACE/scripts/throughput-dashboard.js" "$WORKSPACE"
node "$WORKSPACE/scripts/drift-guard-auto.js" "$WORKSPACE"
```

### Step 3 — Wire decision-audit into high-stakes decisions

```javascript
const { logDecision } = require('./lib/decision-audit');

logDecision({
  task_type: 'code_generation',
  decision: 'spawn CoderAgent',
  reasoning_summary: 'Multi-file edit blocks chat >5s',
  session_channel: 'discord'  // optional
}, workspaceRoot);
```

### Step 4 — Wire failure-tracer into quality validation (optional)

The failure-tracer fires automatically when you call it after scoring subagent output:

```javascript
const { captureFailureTrace } = require('./lib/failure-tracer');

// Call after scoring any subagent output
if (qualityScore < 7) {
  captureFailureTrace('AgentLabel-task', qualityScore, agentOutput, workspaceRoot);
}
```

## Reading the Data

| Path | Contents |
|---|---|
| `memory/dashboards/YYYY-MM-DD.md` | Weekly throughput snapshot |
| `memory/drift-reports/YYYY-MM-DD.md` | Drift compliance report |
| `memory/decisions-audit.jsonl` | Full decision log (JSONL) |
| `memory/traces/[label]-[timestamp].json` | Failure traces |

### Query examples

```bash
# Recent decisions
tail -20 memory/decisions-audit.jsonl | jq .

# All failure traces
ls memory/traces/

# Latest drift report
cat memory/drift-reports/$(ls memory/drift-reports/ | tail -1)
```

## Tool Descriptions

### throughput-dashboard.js
Aggregates weekly metrics: tasks routed, subagents spawned, estimated cost, quality ratio, routing distribution. Reads from `session-metrics.js` (if installed) and `drift-guard-auto.js`. Degrades gracefully if data sources are missing — every section is independent.

### decision-audit.js
Append-only JSONL log at `memory/decisions-audit.jsonl`. Each entry: `{ id, ts, task_type, decision, reasoning_summary, outcome, session_channel }`. Use `updateOutcome(id, 'success', workspaceRoot)` to close the loop after a decision resolves.

### failure-tracer.js
Fires when quality score < 7. Writes structured JSON to `memory/traces/`. Each trace includes: tool call sequence hints, output snippet, inferred failure reason. Use to post-mortem why a subagent underperformed.

### drift-guard-auto.js
Scores recent agent outputs against behavioral rules (sycophancy, social cushioning, unprompted explanations, hallucination hedges). Reads INTENT.md for custom criteria if installed. Writes weekly report to `memory/drift-reports/`.

## References

- `references/throughput-dashboard.js` — Full script implementation
- `references/decision-audit.js` — Full lib implementation
- `references/failure-tracer.js` — Full lib implementation
- `references/drift-guard-auto.js` — Full script implementation
