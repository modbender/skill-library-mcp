# search-openclaw-docs - Agent Workflow

> **Note:** `CLAUDE.md` is a symlink to this file.

## 🚨 MANDATORY Before Config Changes

**Before editing `openclaw.json` (via `config.patch` or `config.apply`):**

1. **Search first:** `node scripts/docs-search.js "<feature>"`
2. **Read the doc:** Use path from search results
3. **Check references:** Read `references/<topic>.md` for patterns
4. **Apply exactly:** Follow documented structure

**Why this matters:** OpenClaw config has specific structures that break silently if wrong. Reference files contain anti-patterns that cause failures.

---

## Structure

```
search-openclaw-docs/
  SKILL.md         # Main skill file
  AGENTS.md        # This workflow guide
  CLAUDE.md        # Symlink to AGENTS.md
  references/      # Common patterns & anti-patterns
  scripts/         # Search and index tools
```

---

## Decision Tree

| Task | Reference File |
|------|----------------|
| Adding/removing agent bindings | `references/config-bindings.md` |
| Enabling/disabling channels | `references/config-channel-management.md` |
| Session reset tuning | `references/config-session-reset.md` |
| Heartbeat configuration | `references/config-heartbeat.md` |
| Config broke after patch | `references/troubleshooting-config-breaks.md` |
| Cron job setup | `references/config-cron.md` |
| Provider configuration | Search docs: "providers" |
| MCP server setup | Search docs: "mcporter" |

---

## Critical Config Patterns (Quick Reference)

### ❌ Common Mistakes

**Bindings:**
```json
// WRONG - will fail
{
  "match": {
    "channelId": "123",
    "guildId": "456"
  }
}
```

**Channel disabling:**
```json
// WRONG - channel stays enabled
{
  "channels": {
    "discord": {
      "allowed": [
        // just removed from list - doesn't disable!
      ]
    }
  }
}
```

**Session reset:**
```json
// WRONG - will replace entire reset config
"agents": {
  "list": [{
    "reset": { "idleMinutes": 10080 }
  }]
}
```

### ✅ Correct Patterns

**Bindings:**
```json
{
  "match": {
    "channel": "discord",
    "peer": { "kind": "channel", "id": "1234567890" }
  }
}
```

**Channel disabling:**
```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1234567890", "allow": false }
      ]
    }
  }
}
```

**Session reset:**
```json
{
  "agents": {
    "list": [{
      "reset": { "idleMinutes": 1440 },
      "resetByChannel": {
        "discord": { "idleMinutes": 10080 }
      }
    }]
  }
}
```

---

## Usage Workflow

### For Config Tasks

1. **Identify the feature** (bindings, channels, sessions, etc.)
2. **Read the reference file** (`references/config-<feature>.md`)
3. **Copy the correct pattern** (don't improvise!)
4. **Use `config.patch`** (safer than `config.apply`)
5. **Verify after restart** (`openclaw status`)

### For Troubleshooting

1. **Search error message:** `node scripts/docs-search.js "error text"`
2. **Check troubleshooting reference:** `references/troubleshooting-*.md`
3. **Read full doc** if needed
4. **Apply fix from reference**

### For General Questions

1. **Search docs:** `node scripts/docs-search.js "topic"`
2. **Read returned file path**
3. **Extract relevant section**

---

## Reference Files (10 embedded patterns)

| Category | Files | Priority |
|----------|-------|----------|
| **Config Patterns** | `config-bindings.md`<br>`config-channel-management.md`<br>`config-session-reset.md`<br>`config-heartbeat.md`<br>`config-cron.md` | CRITICAL |
| **Troubleshooting** | `troubleshooting-config-breaks.md`<br>`troubleshooting-bindings.md` | HIGH |
| **Migration** | `migration-patterns.md`<br>`migration-2026-2-9.md` | MEDIUM |
| **Best Practices** | `best-practices-config.md` | LOW |

---

## When NOT to Use This Skill

- **Personal context/memory** → Use `memory_search` instead
- **Supabase queries** → Use `supabase-postgres-best-practices`
- **Next.js code** → Use `next-best-practices`
- **GitHub operations** → Use `github` skill

---

## Skill Maintenance

**After OpenClaw updates:**
```bash
node scripts/docs-index.js rebuild
```

**Check index health:**
```bash
node scripts/docs-status.js
```

---

*Always read references before making config changes. Prevents silent breakage.*
