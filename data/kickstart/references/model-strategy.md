# Model Strategy — Stop Burning Money

Different tasks need different models. Running your best model for everything is like driving a Ferrari to the corner shop. This guide tells you what to use when.

---

## The Simple Version

| Task | Recommended Model | Why |
|------|------------------|-----|
| Initial setup / onboarding | Claude Opus | Sets personality, gets architecture right. Worth the spend. |
| Daily conversation | Claude Sonnet or Kimi 2.5 | Smart enough for 90% of tasks, fraction of the cost. |
| Heartbeats | Claude Haiku or cheapest available | Just checking if anything needs attention. Don't overthink it. |
| Coding | Claude Sonnet or Deepseek | Both excellent at code. Sonnet for complex, Deepseek for volume. |
| Quick lookups / formatting | Haiku or any fast model | Speed matters more than depth here. |
| Creative writing / strategy | Opus or Sonnet (high thinking) | When quality genuinely matters. |
| Cron jobs / automated scans | Sonnet or Haiku | Depends on complexity. Most scans don't need Opus. |

---

## How to Configure in OpenClaw

### Set Your Primary Model
In your config, set the default model for daily use:
```json
{
  "agents": {
    "defaults": {
      "model": "anthropic/claude-sonnet-4-6-20250218"
    }
  }
}
```

### Set Fallbacks
If your primary model is rate-limited or down, fallbacks kick in:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-6-20250218",
        "fallbacks": [
          "anthropic/claude-haiku-3-5-20241022"
        ]
      }
    }
  }
}
```

### Model for Specific Cron Jobs
Isolated cron jobs can use a different model:
```json
{
  "payload": {
    "kind": "agentTurn",
    "model": "anthropic/claude-haiku-3-5-20241022",
    "message": "Quick check: any urgent emails?"
  }
}
```

### Per-Session Override
Change model mid-session:
```
/model sonnet
```

---

## Cost Reality Check

Rough monthly costs for a single active agent (as of Feb 2026):

| Setup | Approx. Monthly Cost |
|-------|---------------------|
| Opus for everything | $150-300+ |
| Sonnet daily + Opus for important tasks | $40-80 |
| Sonnet daily + Haiku heartbeats | $30-60 |
| Kimi 2.5 (Nvidia free tier) + Haiku heartbeats | $5-15 |

The biggest cost driver is **heartbeats**. If you're running heartbeats every 30 minutes on Opus, that's ~48 Opus calls per day just for background checks. Switch heartbeats to Haiku and you'll save 80%+ on that alone.

---

## The Golden Rule

**Use Opus for setup, Sonnet for daily, Haiku for background.**

Adjust from there based on your budget and what you're actually doing. Most people overspend by 3-5x because they never change the default model.
