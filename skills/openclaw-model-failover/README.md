# openclaw-model-failover

OpenClaw plugin to **auto-detect rate limits/quota errors** and switch sessions to fallback LLMs.

## What it does

- Chooses a model based on a **preferred order** before each agent run.
- Detects rate-limit/quota failures and marks the current model as **temporarily limited**.
- Detects temporary provider/plugin cooldown errors (for example `copilot-proxy` in cooldown) and fails over.
- Optionally patches pinned WhatsApp group sessions so you don’t get stuck with `API rate limit reached` loops.

## Install (dev)

```bash
cd ~/.openclaw/workspace/openclaw-model-failover
openclaw plugins install -l .
openclaw gateway restart
```

## ClawHub

This plugin is published on **clawhub.ai** and installable via:

```bash
clawhub install openclaw-model-failover
```

## Configure

In your OpenClaw config:

```json
{
  "plugins": {
    "entries": {
      "openclaw-model-failover": {
        "enabled": true,
        "config": {
          "modelOrder": [
            "openai-codex/gpt-5.3-codex",
            "anthropic/claude-opus-4-6",
            "github-copilot/claude-sonnet-4.6",
            "google-gemini-cli/gemini-3-pro-preview",
            "anthropic/claude-sonnet-4-6",
            "openai-codex/gpt-5.2",
            "google-gemini-cli/gemini-2.5-pro",
            "perplexity/sonar-deep-research",
            "perplexity/sonar-pro",
            "google-gemini-cli/gemini-2.5-flash",
            "google-gemini-cli/gemini-3-flash-preview"
          ],
          "cooldownMinutes": 300,
          "unavailableCooldownMinutes": 15,
          "patchSessionPins": true,
          "notifyOnSwitch": true,
          "debugLogging": false,
          "debugLogSampleRate": 1.0
        }
      }
    }
  }
}
```

## Status Inspection

Check which models are currently blocked and when they become available again.

### CLI

```bash
# Pretty-print current status
npx tsx status.ts

# Machine-readable JSON output
npx tsx status.ts --json

# Clear a specific model's rate limit
npx tsx status.ts clear openai-codex/gpt-5.3-codex

# Clear all rate-limit entries
npx tsx status.ts clear --all
```

### Programmatic API

```typescript
import { getFailoverStatus, clearModel, clearAllModels } from "./status.js";

// Get structured status snapshot
const status = getFailoverStatus();
console.log(status.activeModel);    // current effective model
console.log(status.blockedCount);   // number of blocked models

// Clear a specific model
clearModel("openai-codex/gpt-5.3-codex");

// Clear all rate limits
clearAllModels();
```

### Example output

```
=== OpenClaw Model Failover Status ===

Active model : anthropic/claude-opus-4-6
Models       : 9 available, 2 blocked
State file   : /home/user/.openclaw/workspace/memory/model-ratelimits.json

Blocked models:
  - openai-codex/gpt-5.3-codex
    Reason      : Provider openai-codex exhausted: 429 Too Many Requests
    Available in: 4h 15m (2026-02-27T08:30:00.000Z)
  - openai-codex/gpt-5.2
    Reason      : Provider openai-codex exhausted: 429 Too Many Requests
    Available in: 4h 15m (2026-02-27T08:30:00.000Z)

Model order:
  [BLOCKED] openai-codex/gpt-5.3-codex
  [OK     ] anthropic/claude-opus-4-6
  [OK     ] github-copilot/claude-sonnet-4.6
  [OK     ] google-gemini-cli/gemini-3-pro-preview
  [OK     ] anthropic/claude-sonnet-4-6
  [BLOCKED] openai-codex/gpt-5.2
  [OK     ] google-gemini-cli/gemini-2.5-pro
  [OK     ] perplexity/sonar-deep-research
  [OK     ] perplexity/sonar-pro
  [OK     ] google-gemini-cli/gemini-2.5-flash
  [OK     ] google-gemini-cli/gemini-3-flash-preview
```

## Usage Metrics

Track failover events for capacity planning and model order optimization.
Events are recorded to an append-only JSONL log file.

### CLI

```bash
# Pretty-print metrics summary
npx tsx metrics.ts

# Machine-readable JSON summary
npx tsx metrics.ts --json

# Show last 20 events
npx tsx metrics.ts tail

# Show last 50 events
npx tsx metrics.ts tail 50

# Clear all metrics
npx tsx metrics.ts reset
```

### Programmatic API

```typescript
import { getMetricsSummary, loadEvents, resetMetrics, formatMetrics } from "./metrics.js";

// Get aggregate summary
const summary = getMetricsSummary();
console.log(summary.totalRateLimits);  // total rate limit hits
console.log(summary.totalFailovers);   // total failover events
console.log(summary.models);           // per-model breakdown
console.log(summary.providers);        // per-provider breakdown

// Get raw events
const events = loadEvents("~/.openclaw/workspace/memory/model-failover-metrics.jsonl");

// Filter by time range
const lastHour = getMetricsSummary({ since: Date.now() / 1000 - 3600 });

// Clear all metrics
resetMetrics();
```

### Configuration

Metrics are enabled by default. To disable or customize:

```json
{
  "metricsEnabled": false,
  "metricsFile": "~/.openclaw/workspace/memory/model-failover-metrics.jsonl"
}
```

### Example output

```
=== OpenClaw Model Failover Metrics ===

Period       : 2026-02-27T00:00:00Z - 2026-02-27T08:30:00Z
Total events : 12
Rate limits  : 8
Auth errors  : 1
Unavailable  : 0
Failovers    : 3

By provider:
  openai-codex                   5 errors  (rate=4 auth=1 unavail=0)
  google-gemini-cli              4 errors  (rate=4 auth=0 unavail=0)

By model:
  google-gemini-cli/gemini-2.5-pro         2 errors  failed-from=1
  openai-codex/gpt-5.2                     2 errors  failed-from=1
  openai-codex/gpt-5.3-codex              3 errors  failed-from=1
  anthropic/claude-opus-4-6                             failed-to=3
```

## Notes / Limitations

- This plugin does not re-run the exact failed turn automatically. It is conservative by default: it only overrides the model when the pinned model is marked limited.
  It prevents future turns from failing by switching the session model.
- The plugin stores state in `~/.openclaw/workspace/memory/model-ratelimits.json` by default.
- Metrics events are logged to `~/.openclaw/workspace/memory/model-failover-metrics.jsonl` by default.

## Roadmap

- Auto-retry same turn after switch (requires deeper agent-loop integration)
- Per-channel routing policies

## Shared Template

For automation that creates GitHub issues, use `src/templates/github-issue-helper.ts`.
It provides `isValidIssueRepoSlug()`, `resolveIssueRepo()`, and `buildGhIssueCreateCommand()`.
