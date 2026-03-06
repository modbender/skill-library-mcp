# Config Pattern: Session Reset

**What:** Configure when conversation sessions reset (lose context).

**When to use:** Controlling session lifetime, per-channel reset policies, memory management.

---

## Critical Pattern: Per-Channel Reset

### ✅ Correct: Global + Channel Overrides

```json
{
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "reset": { "idleMinutes": 1440 },  // Global: 1 day
        "resetByChannel": {
          "discord": { "idleMinutes": 10080 },     // Discord: 7 days
          "telegram": { "idleMinutes": 2880 }      // Telegram: 2 days
        }
      }
    ]
  }
}
```

**Key points:**
- `reset` - Global default
- `resetByChannel` - Per-channel overrides
- Times in minutes (1440 = 1 day, 10080 = 7 days)

---

## ❌ Common Mistakes

### Wrong: Only setting per-channel (no global)

```json
{
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "resetByChannel": {
          "discord": { "idleMinutes": 10080 }
          // Missing global "reset" - uses OpenClaw default
        }
      }
    ]
  }
}
```

**Why it fails:** Channels not in `resetByChannel` use OpenClaw default (often too short).

### Wrong: Replacing entire config with patch

```json
// WRONG when using config.patch
{
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "reset": { "idleMinutes": 10080 }
        // Missing resetByChannel - wipes existing per-channel settings!
      }
    ]
  }
}
```

**Why it fails:** `config.patch` merges, but agent list replaces entirely. Must include all settings.

---

## Reset Strategies

### Short-lived (default behavior)

```json
{
  "reset": { "idleMinutes": 60 }  // 1 hour
}
```

**Use case:** High-traffic channels, quick context switches.

### Medium-lived (recommended default)

```json
{
  "reset": { "idleMinutes": 1440 }  // 1 day
}
```

**Use case:** General purpose, balance memory and continuity.

### Long-lived (for important channels)

```json
{
  "reset": { "idleMinutes": 10080 }  // 7 days
}
```

**Use case:** Personal DMs, main work channels, long-running projects.

---

## Common Time Values

| Minutes | Duration | Use Case |
|---------|----------|----------|
| 60 | 1 hour | High-traffic, quick tasks |
| 240 | 4 hours | Short work sessions |
| 1440 | 1 day | Default recommended |
| 2880 | 2 days | Extended context |
| 10080 | 7 days | Main channels, DMs |
| 43200 | 30 days | Archive mode (rarely resets) |

---

## Full Example: Multi-Agent Setup

```json
{
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "reset": { "idleMinutes": 1440 },
        "resetByChannel": {
          "discord": { "idleMinutes": 10080 },
          "telegram": { "idleMinutes": 1440 }
        }
      },
      {
        "id": "decorly",
        "reset": { "idleMinutes": 1440 },
        "resetByChannel": {
          "telegram": { "idleMinutes": 10080 }
        }
      }
    ]
  }
}
```

---

## Session Cleanup vs Reset

**Two separate mechanisms:**

1. **Session reset** (this file) - When session loses context
2. **Session cleanup** (cron job) - When session metadata is deleted

### Example: 7-day reset + weekly cleanup

```json
{
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "reset": { "idleMinutes": 10080 }  // Context retained 7 days
      }
    ]
  }
}
```

Plus cron job (runs weekly):
```json
{
  "payload": {
    "kind": "systemEvent",
    "text": "Clean up old sessions: keep last 10 runs, age thresholds"
  }
}
```

**Result:** Sessions stay accessible for 7 days, metadata cleaned up weekly to prevent accumulation.

---

## Impact on Memory

**Session reset affects:**
- Conversation context (messages in session)
- Tool call history within session

**Session reset does NOT affect:**
- MEMORY.md
- memory/*.md (daily logs)
- .jsonl transcripts (preserved forever)
- Vector search index (separate)

**Memory is always safe.** Reset only affects active context window.

---

## Verification

```bash
# Check config
openclaw gateway config.get | jq '.agents.list[] | {id, reset, resetByChannel}'

# View session ages
openclaw sessions list --limit 20

# Check last activity
openclaw sessions list --active-minutes 10080  # 7 days
```

---

## References

- OpenClaw docs: `concepts/sessions.md`
- OpenClaw docs: `gateway/configuration.md`
- Related: `troubleshooting-session-accumulation.md`

---

**Use per-channel overrides.** Different channels need different retention policies.
