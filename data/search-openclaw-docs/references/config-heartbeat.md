# Config Pattern: Heartbeat

**What:** Configure periodic agent wake-ups for proactive checks.

**When to use:** Background monitoring, periodic tasks, proactive notifications.

---

## Critical Pattern: Heartbeat Configuration

### ✅ Correct: Full Heartbeat Config

```json
{
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "heartbeat": {
          "enabled": true,
          "intervalMinutes": 30,
          "activeHours": {
            "start": "08:00",
            "end": "23:00",
            "timezone": "Asia/Kolkata"
          },
          "prompt": "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
          "model": "amazon-bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0"
        }
      }
    ]
  }
}
```

**Key points:**
- `enabled` - Turn on/off
- `intervalMinutes` - How often to poll (30 = every 30 minutes)
- `activeHours` - Only wake during these hours (optional)
- `prompt` - Instructions for what to check
- `model` - Override model for heartbeats (use cheaper model)

---

## ❌ Common Mistakes

### Wrong: No activeHours timezone

```json
{
  "heartbeat": {
    "enabled": true,
    "intervalMinutes": 30,
    "activeHours": {
      "start": "08:00",
      "end": "23:00"
      // Missing "timezone" - uses UTC!
    }
  }
}
```

**Why it fails:** Without timezone, uses UTC. Agent wakes at wrong local times.

### Wrong: Too frequent polling

```json
{
  "heartbeat": {
    "enabled": true,
    "intervalMinutes": 5  // WRONG - too expensive, burns tokens
  }
}
```

**Why it fails:** Wastes API calls. Most tasks don't need sub-15min checking.

### Wrong: Using expensive model

```json
{
  "heartbeat": {
    "enabled": true,
    "model": "amazon-bedrock/global.anthropic.claude-opus-4-6-v1"
    // WRONG - opus for heartbeats is overkill
  }
}
```

**Why it fails:** Heartbeats are simple checks. Use Haiku/Flash for 85% cost savings.

---

## Recommended Settings

### Default (balanced)

```json
{
  "heartbeat": {
    "enabled": true,
    "intervalMinutes": 30,
    "activeHours": {
      "start": "08:00",
      "end": "23:00",
      "timezone": "Asia/Kolkata"
    },
    "model": "amazon-bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0"
  }
}
```

### High-frequency (monitoring)

```json
{
  "heartbeat": {
    "enabled": true,
    "intervalMinutes": 15,
    "activeHours": {
      "start": "00:00",
      "end": "23:59",
      "timezone": "Asia/Kolkata"
    },
    "model": "haiku"  // Alias
  }
}
```

### Low-frequency (occasional checks)

```json
{
  "heartbeat": {
    "enabled": true,
    "intervalMinutes": 120,  // 2 hours
    "activeHours": {
      "start": "09:00",
      "end": "18:00",
      "timezone": "Asia/Kolkata"
    },
    "model": "haiku"
  }
}
```

---

## Model Aliases for Heartbeats

| Alias | Full Name | Cost | Use Case |
|-------|-----------|------|----------|
| `haiku` | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | Lowest | ✅ Heartbeats |
| `nova-lite` | `us.amazon.nova-lite-v1:0` | Lowest | ✅ Heartbeats |
| `sonnet` | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | Medium | Main work |
| `opus` | `global.anthropic.claude-opus-4-6-v1` | Highest | Complex tasks |

**Recommendation:** Use `haiku` or `nova-lite` for heartbeats. Save Sonnet/Opus for actual work.

---

## Heartbeat Workflow Files

### HEARTBEAT.md (Workspace File)

```markdown
# HEARTBEAT.md - Gilfoyle Engagement Rules

## Heartbeat Checks

When receiving heartbeat, consider checking:

### System Health
- [ ] Server processes running?
- [ ] Disk space adequate?
- [ ] Memory usage normal?

### Services
- [ ] OpenClaw gateway healthy?
- [ ] Dev servers running (if needed)?

---

If nothing needs attention: **HEARTBEAT_OK**
```

**Location:** `~/.openclaw/workspace-gilfoyle/HEARTBEAT.md`

**Purpose:** Instructions for what agent should check during heartbeats.

---

## Heartbeat vs Cron

**Use heartbeat when:**
- Multiple checks can batch together
- Need conversational context from recent messages
- Timing can drift slightly (every ~30 min is fine)
- Want to reduce API calls by combining checks

**Use cron when:**
- Exact timing matters ("9:00 AM sharp every Monday")
- Task needs isolation from main session
- Want different model/thinking level
- One-shot reminders ("remind me in 20 minutes")

---

## Disabling Heartbeats

### Temporary disable (testing)

```json
{
  "heartbeat": {
    "enabled": false
  }
}
```

### Disable for specific agent

```json
{
  "agents": {
    "list": [
      {
        "id": "decorly",
        "heartbeat": {
          "enabled": false
        }
      }
    ]
  }
}
```

---

## Cost Optimization

### Before: Expensive heartbeats

```json
{
  "heartbeat": {
    "enabled": true,
    "intervalMinutes": 30,
    "model": "sonnet"  // $3/MTok input
  }
}
```

**Monthly cost (30 heartbeats/day × 30 days × 5K tokens):**
- 4.5M tokens/month = ~$13.50

### After: Optimized heartbeats

```json
{
  "heartbeat": {
    "enabled": true,
    "intervalMinutes": 30,
    "activeHours": {
      "start": "08:00",
      "end": "23:00",
      "timezone": "Asia/Kolkata"
    },
    "model": "haiku"  // $0.40/MTok input
  }
}
```

**Monthly cost (20 heartbeats/day × 30 days × 5K tokens):**
- 3M tokens/month = ~$1.20

**Savings: 85% reduction**

---

## Verification

```bash
# Check heartbeat config
openclaw gateway config.get | jq '.agents.list[] | {id, heartbeat}'

# View recent heartbeat sessions
openclaw sessions list --kinds isolated --limit 10

# Check heartbeat timing
journalctl -u openclaw-gateway | grep heartbeat
```

---

## References

- OpenClaw docs: `automation/heartbeat.md`
- OpenClaw docs: `gateway/configuration.md`
- Related: `config-cron.md`, `HEARTBEAT.md` workspace file

---

**Optimize heartbeats: Use Haiku/Nova-Lite + activeHours matching timezone.**
