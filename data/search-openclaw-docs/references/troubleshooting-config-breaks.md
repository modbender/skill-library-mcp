# Troubleshooting: Config Breaks After Changes

**Symptoms:** Config changes don't take effect, gateway won't restart, bindings stop working.

---

## Diagnosis Checklist

### 1. Check Gateway Status

```bash
openclaw gateway status
```

**Look for:**
- Is gateway running?
- Last restart time
- Any error messages

### 2. View Current Config

```bash
openclaw gateway config.get
```

**Verify:**
- Your changes are present
- No unexpected values
- Structure matches documentation

### 3. Check Logs

```bash
journalctl -u openclaw-gateway -n 50 --no-pager
```

**Look for:**
- Parse errors
- Validation failures
- Binding errors

---

## Common Breakages

### Issue: Bindings Not Working

**Symptoms:** Agent doesn't respond in expected channel.

**Causes:**
1. ❌ Wrong binding structure (missing `peer`, wrong fields)
2. ❌ Channel not in allowed list
3. ❌ Agent not restarted after config change

**Fix:**

```bash
# 1. Verify binding structure
openclaw gateway config.get | jq '.agents.list[] | {id, bindings}'

# 2. Check matches reference
cat ~/.openclaw/skills/search-openclaw-docs/references/config-bindings.md

# 3. Restart gateway
openclaw gateway restart
```

### Issue: Channel Disabled But Still Active

**Symptoms:** Messages still arrive from supposedly disabled channel.

**Cause:** ❌ Channel omitted from config instead of `allow: false`.

**Fix:**

```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1468623929550835766", "allow": false }
      ]
    }
  }
}
```

Apply:
```bash
openclaw gateway config.patch --note "Disable decorly Discord channel"
```

### Issue: Session Reset Not Applied

**Symptoms:** Sessions still reset at old interval.

**Cause:** ❌ Forgot `resetByChannel`, only changed global `reset`.

**Fix:**

```json
{
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "reset": { "idleMinutes": 1440 },
        "resetByChannel": {
          "discord": { "idleMinutes": 10080 }
        }
      }
    ]
  }
}
```

### Issue: Config Merge Confusion

**Symptoms:** Patch didn't remove something, or removed too much.

**Cause:** ❌ Misunderstanding `config.patch` vs `config.apply`.

**Rules:**
- `config.patch` **merges** deeply
- But `agents.list` array **replaces** entirely for each agent
- To remove: set explicit `allow: false` or empty array

**Fix:**

```bash
# View what will merge
openclaw gateway config.get > current.json

# Test patch locally (manual merge)
# Then apply

openclaw gateway config.patch
```

---

## Recovery Steps

### If Gateway Won't Start

```bash
# 1. Check config syntax
cat ~/.openclaw/openclaw.json | jq .

# 2. If invalid JSON, restore backup
ls -la ~/.openclaw/openclaw.json.bak*
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json

# 3. Restart
openclaw gateway restart
```

### If Config Changed But Wrong

```bash
# View backups
ls -la ~/.openclaw/openclaw.json.bak*

# Compare
diff ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# Restore if needed
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
openclaw gateway restart
```

---

## Prevention

### Always Use References First

```bash
# Before changing bindings
cat ~/.openclaw/skills/search-openclaw-docs/references/config-bindings.md

# Before changing channels
cat ~/.openclaw/skills/search-openclaw-docs/references/config-channel-management.md

# Before changing sessions
cat ~/.openclaw/skills/search-openclaw-docs/references/config-session-reset.md
```

### Use `config.patch` Not `config.apply`

```bash
# Safer (merges)
openclaw gateway config.patch --note "Add binding"

# Riskier (replaces entire config)
openclaw gateway config.apply
```

### Test in Stages

1. Apply change
2. Verify with `config.get`
3. Restart gateway
4. Test functionality
5. Commit if working

---

## Config Patch Workflow

```bash
# 1. Read reference for feature
cat references/config-<feature>.md

# 2. View current config
openclaw gateway config.get > current.json

# 3. Create patch JSON with ONLY changes
cat > patch.json << 'EOF'
{
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "bindings": [
          {
            "match": {
              "channel": "discord",
              "peer": { "kind": "channel", "id": "1469004697305092288" }
            }
          }
        ]
      }
    ]
  }
}
EOF

# 4. Apply patch
openclaw gateway config.patch --raw "$(cat patch.json)" --note "Add gilfoyle Discord binding"

# 5. Verify
openclaw gateway status
openclaw gateway config.get | jq '.agents.list[] | select(.id=="gilfoyle")'
```

---

## OpenClaw 2026.2.9+ Changes

**New in 2026.2.9:**
1. ✅ Bindings refresh without restart (live updates)
2. ✅ Post-compaction memory preserved
3. ✅ Context overflow handling

**Still required:**
- Gateway restart for most config changes
- Proper binding structure
- Explicit channel disabling

---

## References

- OpenClaw docs: `gateway/configuration.md`
- OpenClaw docs: `gateway/troubleshooting.md`
- Related: `config-bindings.md`, `config-channel-management.md`

---

**Golden rule: Read references → Apply pattern → Verify → Test**
