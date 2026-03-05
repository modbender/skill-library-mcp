# Migration: OpenClaw 2026.2.9 Changes

**Version:** 2026.2.9  
**Release Date:** February 2026  
**Impact:** Critical fixes for session management and config handling

---

## Critical Fixes

### 1. Post-Compaction Amnesia (FIXED ✅)

**Before 2026.2.9:**
- Agents lost memory after context compaction
- Had to re-read workspace files every turn
- Couldn't maintain continuity across long sessions

**After 2026.2.9:**
- Agents remember across compactions
- Workspace context preserved
- Smooth long-running sessions

**Migration:** None required (automatic fix).

---

### 2. Live Config Updates (NEW ✅)

**Before 2026.2.9:**
- Binding changes required gateway restart
- Config changes took effect only after manual restart

**After 2026.2.9:**
- Bindings refresh without restart
- Live config updates (most settings)

**Note:** Some settings still require restart (providers, credentials).

**Migration:**
```bash
# Before: Manual restart needed
openclaw gateway config.patch
openclaw gateway restart

# After: Auto-refresh (bindings)
openclaw gateway config.patch
# Bindings active immediately
```

---

### 3. Context Overflow Recovery (NEW ✅)

**Before 2026.2.9:**
- Oversized tool results caused session failures
- No graceful handling of large outputs

**After 2026.2.9:**
- Automatic truncation of oversized results
- Graceful degradation with warnings
- Session continues smoothly

**Migration:** None required (automatic).

---

## Breaking Changes

None. All changes are backward-compatible.

---

## Recommended Config Updates

### 1. Remove Workarounds

**If you had:**
```json
// Workaround for memory issues (no longer needed)
{
  "agents": {
    "list": [{
      "reset": { "idleMinutes": 60 }  // Short resets to avoid amnesia
    }]
  }
}
```

**Update to:**
```json
{
  "agents": {
    "list": [{
      "reset": { "idleMinutes": 1440 },        // 1 day global
      "resetByChannel": {
        "discord": { "idleMinutes": 10080 }    // 7 days Discord
      }
    }]
  }
}
```

### 2. Optimize Session Reset

**Pattern:** Per-channel reset policies now safe with long windows.

```json
{
  "reset": { "idleMinutes": 1440 },
  "resetByChannel": {
    "discord": { "idleMinutes": 10080 },
    "telegram": { "idleMinutes": 2880 }
  }
}
```

---

## Testing Checklist

After upgrading to 2026.2.9:

- [ ] Long sessions maintain context across compactions
- [ ] Binding changes take effect without restart
- [ ] Large tool outputs handled gracefully
- [ ] Session reset policies work as configured
- [ ] No memory loss in extended conversations

---

## Verification

```bash
# Check version
openclaw --version

# Should show: 2026.2.9 or later

# Test binding live update
openclaw gateway config.patch --raw '{"agents":{"list":[{"id":"agent","bindings":[...]}]}}'
# Send test message immediately (no restart needed)

# Test long session
# Have extended conversation across multiple compactions
# Verify agent remembers early context
```

---

## Rollback (if needed)

```bash
# Restore previous version
# (Consult OpenClaw docs for version management)

# Restore backup config
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
openclaw gateway restart
```

---

## Related Changes

### Session Management
- Session cleanup automation now recommended (see `config-cron.md`)
- Long-running sessions stable (7-day reset safe)

### Config Handling
- `config.patch` behavior unchanged (still merges deeply)
- Backup rotation improved (.bak, .bak.1, .bak.2)

---

## References

- OpenClaw changelog: `/usr/lib/node_modules/openclaw/CHANGELOG.md`
- Related: `config-session-reset.md`, `best-practices-config.md`

---

**Upgrade recommended.** Critical fixes for production stability.
