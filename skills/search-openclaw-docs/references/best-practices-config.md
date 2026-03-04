# Best Practices: OpenClaw Configuration

**Core principles for safe, maintainable OpenClaw configs.**

---

## Golden Rules

### 1. Read References First

**Always:**
```bash
# Before changing anything
ls ~/.openclaw/skills/search-openclaw-docs/references/

# Read the relevant file
cat references/config-bindings.md
```

**Never:**
- Improvise config structure
- Copy-paste without understanding
- Skip the anti-pattern examples

---

### 2. Use config.patch, Not config.apply

**Prefer:**
```bash
openclaw gateway config.patch --note "Add binding"
```

**Avoid:**
```bash
openclaw gateway config.apply  # Replaces entire config!
```

**Why:**
- `config.patch` merges deeply (safer)
- `config.apply` replaces everything (risky)
- Patches keep backups automatically

---

### 3. Structure Over Shortcuts

**Right:**
```json
{
  "match": {
    "channel": "discord",
    "peer": { "kind": "channel", "id": "123" }
  }
}
```

**Wrong:**
```json
{
  "match": {
    "channelId": "123"  // Deprecated, won't work
  }
}
```

**Why:** OpenClaw has specific structures. Shortcuts break silently.

---

### 4. Explicit Over Implicit

**Right:**
```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "123", "allow": false }  // Explicit disable
      ]
    }
  }
}
```

**Wrong:**
```json
{
  "channels": {
    "discord": {
      "allowed": [
        // Just removed "123" - still enabled!
      ]
    }
  }
}
```

**Why:** Config merging means omitting doesn't remove.

---

### 5. Timezone Everything

**Right:**
```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *",
    "tz": "Asia/Kolkata"
  }
}
```

**Wrong:**
```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *"  // Uses UTC!
  }
}
```

**Why:** No timezone = UTC default. Jobs run at wrong times.

---

## Config Workflow

### Standard Change Process

```bash
# 1. Identify feature
# (bindings, channels, sessions, heartbeat, cron)

# 2. Read reference
cat references/config-<feature>.md

# 3. View current config
openclaw gateway config.get > current.json

# 4. Create patch with ONLY changes
cat > patch.json << 'EOF'
{
  "agents": {
    "list": [...]
  }
}
EOF

# 5. Apply patch
openclaw gateway config.patch --raw "$(cat patch.json)" --note "Descriptive note"

# 6. Verify
openclaw gateway status
openclaw gateway config.get | jq '.relevant.path'

# 7. Test
# Send test message, check behavior

# 8. Commit if working
# (OpenClaw auto-backups, but good to commit workspace changes)
```

---

## Common Anti-Patterns

### ❌ Array Confusion

**Problem:**
```json
// WRONG - config.patch replaces entire agents.list
{
  "agents": {
    "list": [
      { "id": "gilfoyle", "bindings": [...] }
      // Missing other agents - they're gone!
    ]
  }
}
```

**Solution:**
- Include ALL agents in patch, even if only changing one
- Or use full `config.apply` when restructuring

### ❌ Missing Nested Structure

**Problem:**
```json
// WRONG
{
  "match": {
    "channel": "discord",
    "id": "123"  // Missing "peer" wrapper
  }
}
```

**Solution:** Always use complete structure from reference.

### ❌ Wrong Payload/SessionTarget Combo

**Problem:**
```json
// WRONG - main requires systemEvent
{
  "payload": { "kind": "agentTurn", "message": "..." },
  "sessionTarget": "main"
}
```

**Solution:**
- `main` → `systemEvent`
- `isolated` → `agentTurn`

### ❌ Hardcoded Values

**Problem:**
```json
// WRONG - token in config
{
  "channels": {
    "discord": {
      "token": "MTIzNDU2Nzg5MDEyMzQ1Njc4.ABCDEF.xyz123"
    }
  }
}
```

**Solution:** Use environment variables or credential files.

---

## Model Selection

### By Use Case

| Task | Recommended Model | Alias |
|------|-------------------|-------|
| Main conversation | Sonnet 4.5 | `sonnet` |
| Complex reasoning | Opus 4.6 | `opus` |
| Heartbeats | Haiku 4.5 | `haiku` |
| Quick checks | Nova Lite | `nova-lite` |
| Background tasks | Haiku/Nova Lite | - |

### Cost Optimization

**Before:**
```json
{
  "agents": {
    "list": [
      {
        "id": "agent",
        "model": "sonnet",
        "heartbeat": { "model": "sonnet" }  // Expensive!
      }
    ]
  }
}
```

**After:**
```json
{
  "agents": {
    "list": [
      {
        "id": "agent",
        "model": "sonnet",
        "heartbeat": { "model": "haiku" }  // 85% cheaper
      }
    ]
  }
}
```

---

## Session Management

### Reset Strategy

**Pattern:**
```json
{
  "reset": { "idleMinutes": 1440 },     // Global: 1 day
  "resetByChannel": {
    "discord": { "idleMinutes": 10080 }, // Discord: 7 days
    "telegram": { "idleMinutes": 1440 }  // Telegram: 1 day
  }
}
```

**Why:**
- Different channels have different context needs
- Personal DMs deserve longer retention
- High-traffic channels need shorter windows

### Cleanup Automation

**Pattern:** Daily cron job at 3 AM

```json
{
  "name": "Session cleanup",
  "schedule": { "kind": "cron", "expr": "0 3 * * *", "tz": "Asia/Kolkata" },
  "payload": {
    "kind": "agentTurn",
    "message": "Clean up old sessions: keep last 10, age thresholds"
  },
  "sessionTarget": "isolated"
}
```

---

## Verification Checklist

After config changes:

- [ ] Gateway started successfully
- [ ] Config contains your changes (`config.get`)
- [ ] No errors in logs (`journalctl -u openclaw-gateway`)
- [ ] Bindings work (test message)
- [ ] Sessions reset as expected
- [ ] Heartbeats fire at right times
- [ ] Cron jobs scheduled correctly

---

## Recovery

### If Something Breaks

```bash
# 1. Check status
openclaw gateway status

# 2. View logs
journalctl -u openclaw-gateway -n 50

# 3. Compare config
diff ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# 4. Restore if needed
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
openclaw gateway restart

# 5. Read troubleshooting reference
cat references/troubleshooting-config-breaks.md
```

---

## References by Topic

| Topic | Reference File |
|-------|----------------|
| Bindings | `config-bindings.md` |
| Channels | `config-channel-management.md` |
| Sessions | `config-session-reset.md` |
| Heartbeat | `config-heartbeat.md` |
| Cron | `config-cron.md` |
| Troubleshooting | `troubleshooting-config-breaks.md` |

---

**Core principle: Structure matters. Follow references exactly.**
