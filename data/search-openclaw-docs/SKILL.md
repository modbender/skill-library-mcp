---
name: search-openclaw-docs
description: MANDATORY before any openclaw.json changes. Prevents config breakage via embedded anti-patterns and correct patterns. Use when configuring OpenClaw (bindings, channels, sessions, cron, heartbeat) or troubleshooting config issues.
metadata:
  openclaw:
    emoji: "📚"
    homepage: https://github.com/karmanverma/search-openclaw-docs
    requires:
      bins: ["node"]
    install:
      - id: "deps"
        kind: "npm"
        package: "better-sqlite3"
        label: "Install better-sqlite3 (SQLite bindings)"
    postInstall: "node scripts/docs-index.js rebuild"
---

# OpenClaw Documentation Search + Config Patterns

**MANDATORY before changing `openclaw.json`** - Embedded patterns prevent silent config breakage.

**Two modes:**
1. **Embedded references** (instant) - Common config patterns with anti-patterns
2. **Doc search** (fallback) - Full OpenClaw documentation index

---

## 🚨 CRITICAL: Read AGENTS.md First

Before using this skill:

```bash
cat ~/.openclaw/skills/search-openclaw-docs/AGENTS.md
```

**Contains:**
- Mandatory workflow for config changes
- Decision tree (which reference to read)
- Critical anti-patterns overview
- When NOT to use this skill

---

## Decision Tree

| Task | Action |
|------|--------|
| Adding/removing agent bindings | Read `references/config-bindings.md` |
| Enabling/disabling channels | Read `references/config-channel-management.md` |
| Session reset tuning | Read `references/config-session-reset.md` |
| Heartbeat configuration | Read `references/config-heartbeat.md` |
| Cron job setup | Read `references/config-cron.md` |
| Config broke after patch | Read `references/troubleshooting-config-breaks.md` |
| Best practices overview | Read `references/best-practices-config.md` |
| Migration (2026.2.9) | Read `references/migration-2026-2-9.md` |
| Other config questions | Search docs (see below) |

---

## Embedded References (8 files)

**Config Patterns:**
- `config-bindings.md` - Agent routing (CRITICAL)
- `config-channel-management.md` - Enable/disable channels (CRITICAL)
- `config-session-reset.md` - Session lifetime policies (HIGH)
- `config-heartbeat.md` - Proactive monitoring (MEDIUM)
- `config-cron.md` - Scheduled tasks (MEDIUM)

**Support:**
- `troubleshooting-config-breaks.md` - Fix broken configs (CRITICAL)
- `best-practices-config.md` - Safe patterns (HIGH)
- `migration-2026-2-9.md` - Version updates (MEDIUM)

**Each reference contains:**
- ✅ Correct pattern
- ❌ Common anti-patterns
- Why it breaks
- Examples

---

## When to Use

| Scenario | Action |
|----------|--------|
| Before editing `openclaw.json` | ✅ Read relevant reference first |
| Config changes not working | ✅ Read troubleshooting reference |
| Learning OpenClaw config | ✅ Read best practices reference |
| Personal memory/context | ❌ Use `memory_search` instead |
| Supabase/database work | ❌ Use `supabase-postgres-best-practices` |
| Next.js code patterns | ❌ Use `next-best-practices` |

---

## Doc Search (Fallback)

For topics not in references, search full docs:

```bash
# Search
node ~/.openclaw/skills/search-openclaw-docs/scripts/docs-search.js "discord requireMention"

# Check index health
node ~/.openclaw/skills/search-openclaw-docs/scripts/docs-status.js

# Rebuild (after OpenClaw update)
node ~/.openclaw/skills/search-openclaw-docs/scripts/docs-index.js rebuild
```

## Usage Examples

```bash
# Config question
node scripts/docs-search.js "discord requireMention"

# Troubleshooting  
node scripts/docs-search.js "webhook not working"

# More results
node scripts/docs-search.js "providers" --top=5

# JSON output
node scripts/docs-search.js "heartbeat" --json
```

## Output Format

```
🔍 Query: discord only respond when mentioned

🎯 Best match:
   channels/discord.md
   "Discord (Bot API)"
   Keywords: discord, requiremention
   Score: 0.70

📄 Also relevant:
   concepts/groups.md (0.66)

💡 Read with:
   cat /usr/lib/node_modules/openclaw/docs/channels/discord.md
```

## How It Works

- FTS5 keyword matching on titles, headers, config keys
- Handles camelCase terms like `requireMention`
- Porter stemming for flexible matching
- No network calls - fully offline

## Index Location

- **Index**: `~/.openclaw/docs-index/openclaw-docs.sqlite`
- **Docs**: `/usr/lib/node_modules/openclaw/docs/`

Index is built locally from your OpenClaw version.

## Troubleshooting

### No results / wrong results

```bash
# 1. Check index exists
node scripts/docs-status.js

# 2. Rebuild if stale
node scripts/docs-index.js rebuild

# 3. Try exact config terms (camelCase matters)
node scripts/docs-search.js "requireMention"

# 4. Try broader terms
node scripts/docs-search.js "discord"
```

## Integration

```javascript
const { search } = require('./lib/search');
const INDEX = process.env.HOME + '/.openclaw/docs-index/openclaw-docs.sqlite';

const results = await search(INDEX, "discord webhook");
// results[0].path → full path to read
```
