---
name: cost-guardian
description: "Prevents wasteful token spend. Reviews cron jobs, polling intervals, and model selection before they go live. Recommends cost-saving changes and flags expensive patterns. Invoke when creating cron jobs, workflows, or when asked about costs/usage."
user-invocable: true
---

# Cost Guardian

Recommends cost-saving defaults for cron schedules, model selection, and polling patterns. **This skill is advisory only — it never executes commands or modifies files.**

## Scope

This skill **only provides recommendations**. It will:

- Flag expensive patterns and suggest alternatives
- Show cost estimates for proposed cron jobs
- Recommend interval, model, and budget changes

It will **not**:

- Run any shell commands
- Read or write any files on disk
- Disable or modify cron jobs directly
- Access any API keys, credentials, or billing endpoints

All actions are the user's responsibility.

## Rules — ALWAYS apply these when reviewing

### 1. Cron Polling Intervals

Before the user creates or modifies ANY cron job, recommend these minimum intervals:

| Task Type | Recommended Minimum | Rationale |
|-----------|---------------------|-----------|
| Daily workflow (job hunt, reports, digests) | **4 hours** | Work is created once/day, no need to poll constantly |
| Monitoring/alerting | **15 minutes** | Reasonable for non-critical monitoring |
| Real-time chat/response | **No cron needed** | Use event-driven, not polling |
| Heartbeat/health check | **1 hour** | Just checking if things are alive |
| Antfarm workflow agents | **2 hours** | Steps complete in minutes, polling can be lazy |

**Flag any polling interval under 5 minutes** as expensive. Show the cost estimate and let the user decide.

### 2. Model Selection for Cron Jobs

Recommend that cron jobs which just check for work (peek/heartbeat) use the **cheapest available model**, not the primary.

| Task | Recommended Model |
|------|------------------|
| Heartbeat / peek for work | Cheapest available (e.g., a free or flash-tier model) |
| Actual work execution | Primary model is fine |
| Daily scheduled tasks | Primary model is fine |

**Flag expensive models used for heartbeat polling.** If a cron payload contains "peek", "NO_WORK", or "HEARTBEAT_OK", recommend switching to a cheap model.

### 3. Cost Estimation — Show Before Creating

Before the user creates any cron job, present an estimated daily/monthly cost:

```
Estimated cost:
  Calls/day: {24 * 60 / interval_minutes}
  ~tokens/call: {estimate based on payload size}
  Model rate: {input + output per M tokens}
  Daily cost: ${calls * tokens * rate}
  Monthly cost: ${daily * 30}
```

Recommend user confirmation if the monthly estimate exceeds $5.

### 4. Budget Alerts

Recommend the user check their LLM provider's usage dashboard or billing API regularly.

**Suggested alert thresholds:**
- Daily spend > $5 → WARN
- Daily spend > $15 → CRITICAL — recommend pausing non-essential crons
- Weekly spend > $30 → Recommend reviewing all cron jobs for optimizations

### 5. Antfarm Workflow Guard

When the user sets up antfarm workflows, recommend:
- Setting polling to **2 hours** (`7200000` ms) instead of the 5-minute default
- Using a cheap model for peek/heartbeat payloads
- Using the primary model only for actual step execution (claim + work)
- Disabling polling crons after the workflow completes

### 6. Audit Checklist

When the user asks to audit costs, suggest they:

1. Check provider spend via their billing dashboard
2. List all active cron jobs
3. Flag any job polling more frequently than its category minimum
4. Flag any heartbeat job using an expensive model
5. Calculate projected monthly cost
6. Apply recommended changes

## Example Intervention

**User says:** "Set up a cron to check for new emails every minute"

**Cost Guardian response:**
> Checking every minute with a premium model would cost ~$8-15/day (~$250-450/month).
>
> Recommended: Every 15 minutes with a free/flash-tier model.
> That's $0/day and you'll still catch emails within 15 min.
>
> Would you like to use those settings instead?

